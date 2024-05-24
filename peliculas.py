from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum

class Tipo(str, Enum): 
    serie = "Serie"
    pelicula = "Película"

class Categoria(BaseModel): 
    ID : str
    nombre : str
    descripcion : str | None = None

class Pelicula(BaseModel): 
    ID : str
    nombre : str
    sinopsis : str
    categoria : Categoria
    estreno : datetime
    tipo : Tipo
    duracion: float 
    capitulos: int
    calificacion: int
    @field_validator('nombre')
    def verificar(cls, nombre): 
        if len(nombre) > 255: raise ValueError('El nombre no puede tener más de 255 caracteres')
        return nombre
    @field_validator('capitulos')
    def realidad(cls, capitulos): 
        if capitulos < 0: raise ValueError('La cantidad de capítulos no pueden ser negativos')
        return capitulos
    @field_validator('duracion')
    def realidad(cls, duracion): 
        if duracion <= 0: raise ValueError('La duración promedio no pueden ser menor o igual a 0')
        return duracion
    @field_validator('calificacion')
    def rango(cls, calificacion): 
        if calificacion < 1: raise ValueError('La calificación no puede ser menor a 1')
        if calificacion > 5: raise ValueError('La calificación no puede ser mayor a 5')
        return calificacion

peliculas : list[Pelicula] = []
categorias : list[Categoria] = []

app = FastAPI()

@app.get('/Tipos', status_code=status.HTTP_302_FOUND)
async def Buscar_tipos(): 
    return [Tipo.pelicula, Tipo.serie]

@app.get('/categorias', status_code=status.HTTP_302_FOUND)
async def listar_categorias(): 
    return categorias

@app.post('/categoria', status_code=status.HTTP_201_CREATED)
async def crear_categoria(categoria : Categoria): 
    for esto in categorias: 
        if esto.ID == categoria.ID: 
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE, 
                detail={'Mensaje': 'No se puede crear una categoria con una id que ya existe'}
            )
    categorias.append(categoria)
    return categoria

@app.get('/peliculas', status_code=status.HTTP_302_FOUND)
async def listar_peliculas(): 
    return peliculas

@app.post('/pelicula', status_code=status.HTTP_201_CREATED)
async def agregar_pelicula(pelicula : Pelicula): 
    for esto in peliculas: 
        if esto.ID == pelicula.ID: 
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE, 
                detail={'Mensaje': 'No se puede agregar una película con una id repetida'}
            )
    if pelicula.tipo == Tipo.serie and pelicula.capitulos == 0: 
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, 
            detail={'Mensaje': 'Una serie no puede tener 0 capítulos'}
        )
    if pelicula.tipo == Tipo.pelicula and pelicula.capitulos != 0: 
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, 
            detail={'Mensaje': 'Una película no puede tener capítulos'}
        )
    pelicula.estreno.month
    peliculas.append(pelicula)
    return pelicula

@app.get('/pelicula/{id}', status_code=status.HTTP_302_FOUND)
async def buscar_pelicula(id : str): 
    for esto in peliculas: 
        if esto.ID == id: return esto
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail={'Mensaje': 'No existe una película con tal id'}
    )

@app.put('/pelicula/{id}', status_code=status.HTTP_202_ACCEPTED)
async def modificar_pelicula(id : str, pelicula : Pelicula): 
    for i in range(len(peliculas)): 
        if peliculas[i].ID == pelicula.ID: 
            if pelicula.ID == id: 
                peliculas[i] = pelicula
                return peliculas[i]
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE, 
                detail={'Mensaje': 'La id de la película no puede ser diferente a la id del parámetro'}
            )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail={'Mensaje': 'No se pudo encontrar una película con tal id'}
    )

@app.delete('/pelicula/{id}', status_code=status.HTTP_202_ACCEPTED)
async def eliminar_pelicula(id : str): 
    for i in range(len(peliculas)): 
        if peliculas[i].ID == id: 
            pelicula = peliculas[i]
            peliculas.remove(peliculas[i])
            return pelicula
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail={'Mensaje': 'No se pudo encontrar una película con tal id'}
    )

@app.get('/peliculas/menor', status_code=status.HTTP_302_FOUND)
async def buscar_menor(): 
    return sorted(peliculas, key=lambda x: x.calificacion)[0]

@app.get('/peliculas/mayor', status_code=status.HTTP_302_FOUND)
async def buscar_mayor(): 
    return sorted(peliculas, key=lambda x: x.calificacion)[-1]

@app.get('/peliculas/promedio_series', status_code=status.HTTP_302_FOUND)
async def buscar_promedio_series(): 
    pass

@app.get('/peliculas/estrenos', status_code=status.HTTP_302_FOUND)
async def buscar_estrenos_mes():
    return filter(lambda x: x.estreno.month == datetime.now().month and x.estreno.year == datetime.now().year, peliculas)