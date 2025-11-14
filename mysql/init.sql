-- Inicialización de la base de datos "obligatorio"
DROP DATABASE IF EXISTS `obligatorio`;
CREATE DATABASE `obligatorio`;
USE `obligatorio`;

-- Crear esquema (tablas)
CREATE TABLE obligatorio.login(
    correo VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL,
    PRIMARY KEY (correo)
);

CREATE TABLE obligatorio.participante(
    ci VARCHAR(50) NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    fecha_nac DATE,
    genero ENUM('masculino', 'femenino', 'otro'),
    PRIMARY KEY (ci)
);

CREATE TABLE obligatorio.datos_cuenta(
    email VARCHAR(50) NOT NULL,
    ci VARCHAR(50) NOT NULL,
    rol ENUM('alumno', 'docente') NOT NULL,
    PRIMARY KEY (email),
    FOREIGN KEY (ci) REFERENCES participante (ci)
);

CREATE TABLE obligatorio.facultad(
    id_facultad INT AUTO_INCREMENT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    PRIMARY KEY (id_facultad)
);

CREATE TABLE obligatorio.programa_academico(
    nombre_programa VARCHAR(100) NOT NULL,
    id_facultad INT NOT NULL,
    tipo ENUM('grado', 'posgrado') NOT NULL,
    PRIMARY KEY (nombre_programa),
    FOREIGN KEY(id_facultad) REFERENCES facultad (id_facultad)
);

CREATE TABLE obligatorio.cuenta_programa_academico(
    email VARCHAR(50) NOT NULL,
    nombre_programa VARCHAR(100) NOT NULL,
    PRIMARY KEY(email,nombre_programa),
    FOREIGN KEY (email) REFERENCES datos_cuenta (email),
    FOREIGN KEY (nombre_programa) REFERENCES programa_academico (nombre_programa)
);

CREATE TABLE obligatorio.edificio(
    nombre_edificio VARCHAR(50) NOT NULL,
    direccion VARCHAR(100) NOT NULL,
    departamento VARCHAR(50) NOT NULL,
    PRIMARY KEY (nombre_edificio)
);

CREATE TABLE obligatorio.sala(
    nombre_sala CHAR(2) NOT NULL,
    edificio VARCHAR(50) NOT NULL,
    capacidad INT NOT NULL,
    tipo_sala ENUM('libre', 'posgrado', 'docente') NOT NULL,
    PRIMARY KEY (nombre_sala, edificio),
    FOREIGN KEY (edificio) REFERENCES edificio (nombre_edificio)
);

CREATE TABLE obligatorio.turno(
    id_turno INT NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    PRIMARY KEY (id_turno)
);

CREATE TABLE obligatorio.reserva(
    id_reserva INT NOT NULL,
    nombre_sala CHAR(2) NOT NULL,
    edificio VARCHAR(50) NOT NULL,
    fecha DATE NOT NULL,
    id_turno INT NOT NULL,
    estado ENUM('cancelada', 'activa', 'sin asistencia', 'finalizada'),
    PRIMARY KEY (id_reserva),
    FOREIGN KEY (nombre_sala, edificio) REFERENCES sala (nombre_sala,edificio),
    FOREIGN KEY (id_turno) REFERENCES turno (id_turno)
);

CREATE TABLE obligatorio.reserva_cuenta(
    participante_ci VARCHAR(50) NOT NULL,
    id_reserva INT NOT NULL,
    fecha_solicitud_reserva DATE NOT NULL,
    asistencia BOOLEAN,
    PRIMARY KEY (participante_ci,id_reserva),
    FOREIGN KEY (participante_ci) REFERENCES participante (ci),
    FOREIGN KEY (id_reserva) REFERENCES reserva (id_reserva)
);

CREATE TABLE obligatorio.sancion_cuenta(
    participante_ci VARCHAR(50) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    PRIMARY KEY (participante_ci, fecha_inicio, fecha_fin),
    FOREIGN KEY (participante_ci) REFERENCES participante (ci)
);

-- Datos de ejemplo
INSERT INTO participante (ci, nombre, apellido, fecha_nac, genero)
VALUES
    (5495057,'Matías','Hernandez','2004-12-05','masculino'),
    (5474899,'Sofía','Lopéz','2004-01-01','femenino'),
    (5334656,'José','Artigas','2003-05-01','masculino'),
    (5502347,'Luis','Suarez','2005-04-03','masculino'),
    (4932331,'Oscar','Tabarez','1995-06-17','masculino'),
    (4889765,'Hana','Arendt', '1988-08-23','femenino'),
    (4777897,'Roberto','Musso','1985-02-18','masculino');

INSERT INTO datos_cuenta (email, ci, rol)
VALUES
    ('matias.hernanez@correo.ucu.edu.uy',5495057,'alumno'),
    ('sofia.lopez@correo.ucu.edu.uy',5474899,'alumno'),
    ('jose.artigas@correo.ucu.edu.uy',5334656,'alumno'),
    ('luis.suarez@correo.ucu.edu.uy',5502347,'alumno'),
    ('l.suarez@ucu.edu.uy',5502347,'docente'),
    ('oscar.tabarez@correo.ucu.edu.uy',4932331,'docente'),
    ('hana.arendt@correo.ucu.edu.uy',4889765,'docente'),
    ('roberto.musso@correo.ucu.edu.uy',4777897,'docente');

INSERT INTO turno (id_turno, hora_inicio, hora_fin)
VALUES
    (1,'08:00','09:00'),
    (2,'09:00','10:00'),
    (3,'10:00','11:00'),
    (4,'11:00','12:00'),
    (5,'12:00','13:00'),
    (6,'13:00','14:00'),
    (7,'14:00','15:00'),
    (8,'15:00','16:00'),
    (9,'16:00','17:00'),
    (10,'17:00','18:00'),
    (11,'18:00','19:00'),
    (12,'19:00','20:00'),
    (13,'20:00','21:00'),
    (14,'21:00','22:00'),
    (15,'22:00','23:00');

INSERT INTO login (correo, password)
VALUES
    ('mailejemplo@ucu.edu.uy','obligatorio2025');

INSERT INTO facultad (id_facultad, nombre)
VALUES
    (1,'Facultad de ingeniería y tecnologías'),
    (2,'Facultad de Psicología y Bienestar Humano');

-- Normalicé el nombre para evitar errores de FK
INSERT INTO programa_academico (nombre_programa, id_facultad, tipo)
VALUES
    ('Ingeniería en Informática', 1,'grado'),
    ('Licenciatura en Psicología',2,'grado'),
    ('Maestría en salud y PNIE', 2, 'posgrado');

INSERT INTO cuenta_programa_academico(email, nombre_programa)
VALUES
    ('matias.hernanez@correo.ucu.edu.uy','Ingeniería en Informática'),
    ('sofia.lopez@correo.ucu.edu.uy','Licenciatura en Psicología'),
    ('jose.artigas@correo.ucu.edu.uy','Maestría en salud y PNIE'),
    ('luis.suarez@correo.ucu.edu.uy','Ingeniería en Informática'),
    ('l.suarez@ucu.edu.uy','Ingeniería en Informática'),
    ('oscar.tabarez@correo.ucu.edu.uy','Ingeniería en Informática'),
    ('hana.arendt@correo.ucu.edu.uy','Maestría en salud y PNIE'),
    ('roberto.musso@correo.ucu.edu.uy','Licenciatura en Psicología');

INSERT INTO edificio(nombre_edificio, direccion, departamento)
VALUES
    ('Edificio Mullin','Comandante Braga 2745','Montevideo'),
    ('Edificio Sacre Coeur','Av. 8 de Octubre 2738','Montevideo');

INSERT INTO sala(nombre_sala, edificio, capacidad, tipo_sala)
VALUES
    ('1A','Edificio Mullin',5,'docente'),
    ('1B','Edificio Mullin',3,'posgrado'),
    ('2A','Edificio Mullin',4,'libre'),
    ('1A','Edificio Sacre Coeur',3,'libre'),
    ('1B','Edificio Sacre Coeur',5,'docente');

-- Usuario para la aplicación
CREATE USER IF NOT EXISTS 'appuser'@'%' IDENTIFIED BY 'apppassword';
GRANT ALL PRIVILEGES ON obligatorio.* TO 'appuser'@'%';
FLUSH PRIVILEGES;