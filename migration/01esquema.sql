-- =========================================================
-- ESQUEMA OLTP / RAW STAGING: Cooperativa El Volcán (Nicaragua)
-- =========================================================

DROP TABLE IF EXISTS embarques_exportacion CASCADE;
DROP TABLE IF EXISTS procesamiento_beneficio CASCADE;
DROP TABLE IF EXISTS lotes_acopio CASCADE;
DROP TABLE IF EXISTS clima_zonas_cafetaleras CASCADE;
DROP TABLE IF EXISTS cuadrillas_corte CASCADE;
DROP TABLE IF EXISTS beneficios CASCADE;
DROP TABLE IF EXISTS variedades_cafe CASCADE;
DROP TABLE IF EXISTS fincas CASCADE;

CREATE TABLE fincas (
    id_finca INT PRIMARY KEY,
    nombre_finca VARCHAR(100) NOT NULL,
    id_productor INT NOT NULL,
    nombre_productor VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL CHECK (region IN ('Jinotega', 'Matagalpa', 'Nueva Segovia - Dipilto', 'Madriz')),
    municipio VARCHAR(50) NOT NULL,
    latitud DECIMAL(9,6) NOT NULL,
    longitud DECIMAL(9,6) NOT NULL,
    altitud_msnm INT NOT NULL,
    area_manzanas DECIMAL(6,2) NOT NULL
);

CREATE TABLE variedades_cafe (
    id_variedad INT PRIMARY KEY,
    nombre_variedad VARCHAR(50) NOT NULL,
    especie VARCHAR(30) NOT NULL DEFAULT 'Coffea Arabica',
    perfil_sensorial_base VARCHAR(100) NOT NULL,
    resistencia_roya VARCHAR(20) NOT NULL CHECK (resistencia_roya IN ('alta', 'media', 'susceptible')),
    rendimiento_promedio_qq_mz DECIMAL(5,2) NOT NULL
);

CREATE TABLE beneficios (
    id_beneficio INT PRIMARY KEY,
    nombre_beneficio VARCHAR(100) NOT NULL,
    tipo_beneficio VARCHAR(20) NOT NULL CHECK (tipo_beneficio IN ('humedo', 'seco')),
    municipio VARCHAR(50) NOT NULL,
    latitud DECIMAL(9,6) NOT NULL,
    longitud DECIMAL(9,6) NOT NULL,
    capacidad_quintales_dia DECIMAL(10,2) NOT NULL,
    costo_procesamiento_qq DECIMAL(8,2) NOT NULL
);

CREATE TABLE cuadrillas_corte (
    id_cuadrilla INT PRIMARY KEY,
    nombre_cuadrilla VARCHAR(100) NOT NULL,
    capacidad_recolectores INT NOT NULL,
    rendimiento_latas_dia DECIMAL(8,2) NOT NULL,
    costo_jornal_dia DECIMAL(8,2) NOT NULL,
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('activa', 'descanso', 'asignada'))
);

CREATE TABLE clima_zonas_cafetaleras (
    fecha DATE PRIMARY KEY,
    region VARCHAR(50) NOT NULL,
    precipitacion_mm DECIMAL(6,2) NOT NULL,
    temperatura_media_c DECIMAL(4,1) NOT NULL,
    temperatura_min_c DECIMAL(4,1) NOT NULL,
    temperatura_max_c DECIMAL(4,1) NOT NULL,
    humedad_relativa_pct DECIMAL(5,2) NOT NULL,
    condicion_clima VARCHAR(20) NOT NULL CHECK (condicion_clima IN ('soleado', 'nublado', 'llovizna', 'temporal'))
);

CREATE TABLE lotes_acopio (
    id_lote INT PRIMARY KEY,
    id_finca INT NOT NULL REFERENCES fincas(id_finca),
    id_variedad INT NOT NULL REFERENCES variedades_cafe(id_variedad),
    id_cuadrilla INT REFERENCES cuadrillas_corte(id_cuadrilla),
    fecha_corte DATE NOT NULL,
    peso_cereza_kg DECIMAL(10,2) NOT NULL CHECK (peso_cereza_kg > 0),
    humedad_porcentaje DECIMAL(5,2) NOT NULL,
    puntaje_catacion_scaa DECIMAL(4,2) NOT NULL,
    certificacion VARCHAR(50) NOT NULL,
    notas_catacion TEXT,
    costo_recoleccion_nio DECIMAL(10,2) NOT NULL,
    estado_lote VARCHAR(30) NOT NULL CHECK (estado_lote IN ('recolectado', 'en_beneficio_humedo', 'en_secado', 'listo_exportacion', 'descartado'))
);

CREATE TABLE procesamiento_beneficio (
    id_proceso INT PRIMARY KEY,
    id_lote INT NOT NULL REFERENCES lotes_acopio(id_lote),
    id_beneficio INT NOT NULL REFERENCES beneficios(id_beneficio),
    etapa VARCHAR(30) NOT NULL CHECK (etapa IN ('despulpado', 'fermentacion', 'secado_patio', 'trillado', 'clasificacion')),
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP,
    temperatura_fermentacion_c DECIMAL(4,1),
    merma_porcentaje DECIMAL(5,2) NOT NULL,
    peso_salida_kg DECIMAL(10,2) NOT NULL,
    observaciones_proceso TEXT
);



CREATE TABLE embarques_exportacion (
    id_embarque INT PRIMARY KEY,
    id_lote INT NOT NULL REFERENCES lotes_acopio(id_lote),
    numero_contenedor VARCHAR(20) NOT NULL,
    puerto_salida VARCHAR(100) NOT NULL,
    pais_destino VARCHAR(50) NOT NULL,
    cliente_comprador VARCHAR(100) NOT NULL,
    fecha_embarque DATE NOT NULL,
    peso_oro_quintales DECIMAL(8,2) NOT NULL,
    precio_quintal_usd DECIMAL(8,2) NOT NULL,
    flete_transporte_usd DECIMAL(8,2) NOT NULL,
    total_usd DECIMAL(10,2) NOT NULL
);
