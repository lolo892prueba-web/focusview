-- =============================================
-- Base de Datos FocusView - SQL Server
-- Esquema completo para almacenar todo el contenido
-- =============================================

-- Crear la base de datos
CREATE DATABASE FocusViewDB;
GO

USE FocusViewDB;
GO

-- =============================================
-- TABLA DE USUARIOS
-- =============================================
CREATE TABLE Usuarios (
    UsuarioID INT IDENTITY(1,1) PRIMARY KEY,
    NombreUsuario NVARCHAR(50) NOT NULL UNIQUE,
    NombreCompleto NVARCHAR(100) NOT NULL,
    Email NVARCHAR(100) NOT NULL UNIQUE,
    Avatar NVARCHAR(200),
    FechaRegistro DATETIME2 DEFAULT GETDATE(),
    Activo BIT DEFAULT 1,
    CONSTRAINT CK_Email CHECK (Email LIKE '%@%.%')
);
GO

-- =============================================
-- TABLA DE CATEGORÍAS
-- =============================================
CREATE TABLE Categorias (
    CategoriaID INT IDENTITY(1,1) PRIMARY KEY,
    Nombre NVARCHAR(50) NOT NULL UNIQUE,
    Descripcion NVARCHAR(200),
    Icono NVARCHAR(50),
    Color NVARCHAR(7) DEFAULT '#2563eb',
    Activa BIT DEFAULT 1,
    FechaCreacion DATETIME2 DEFAULT GETDATE()
);
GO

-- =============================================
-- TABLA DE PUBLICACIONES
-- =============================================
CREATE TABLE Publicaciones (
    PublicacionID INT IDENTITY(1,1) PRIMARY KEY,
    UsuarioID INT NOT NULL,
    Titulo NVARCHAR(200) NOT NULL,
    Descripcion NVARCHAR(500),
    ImagenURL NVARCHAR(500) NOT NULL,
    ImagenNombre NVARCHAR(200),
    ImagenTamaño BIGINT,
    CategoriaID INT NOT NULL,
    Likes INT DEFAULT 0,
    Vistas INT DEFAULT 0,
    Guardados INT DEFAULT 0,
    Compartidos INT DEFAULT 0,
    FechaPublicacion DATETIME2 DEFAULT GETDATE(),
    FechaActualizacion DATETIME2 DEFAULT GETDATE(),
    Activa BIT DEFAULT 1,
    CONSTRAINT FK_Publicaciones_Usuarios FOREIGN KEY (UsuarioID) REFERENCES Usuarios(UsuarioID),
    CONSTRAINT FK_Publicaciones_Categorias FOREIGN KEY (CategoriaID) REFERENCES Categorias(CategoriaID)
);
GO

-- =============================================
-- TABLA DE LIKES
-- =============================================
CREATE TABLE Likes (
    LikeID INT IDENTITY(1,1) PRIMARY KEY,
    UsuarioID INT NOT NULL,
    PublicacionID INT NOT NULL,
    FechaLike DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_Likes_Usuarios FOREIGN KEY (UsuarioID) REFERENCES Usuarios(UsuarioID),
    CONSTRAINT FK_Likes_Publicaciones FOREIGN KEY (PublicacionID) REFERENCES Publicaciones(PublicacionID),
    CONSTRAINT UK_Likes UNIQUE (UsuarioID, PublicacionID)
);
GO

-- =============================================
-- TABLA DE GUARDADOS
-- =============================================
CREATE TABLE Guardados (
    GuardadoID INT IDENTITY(1,1) PRIMARY KEY,
    UsuarioID INT NOT NULL,
    PublicacionID INT NOT NULL,
    FechaGuardado DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_Guardados_Usuarios FOREIGN KEY (UsuarioID) REFERENCES Usuarios(UsuarioID),
    CONSTRAINT FK_Guardados_Publicaciones FOREIGN KEY (PublicacionID) REFERENCES Publicaciones(PublicacionID),
    CONSTRAINT UK_Guardados UNIQUE (UsuarioID, PublicacionID)
);
GO

-- =============================================
-- TABLA DE COMPARTIDOS
-- =============================================
CREATE TABLE Compartidos (
    CompartidoID INT IDENTITY(1,1) PRIMARY KEY,
    UsuarioID INT NOT NULL,
    PublicacionID INT NOT NULL,
    Plataforma NVARCHAR(50),
    FechaCompartido DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_Compartidos_Usuarios FOREIGN KEY (UsuarioID) REFERENCES Usuarios(UsuarioID),
    CONSTRAINT FK_Compartidos_Publicaciones FOREIGN KEY (PublicacionID) REFERENCES Publicaciones(PublicacionID)
);
GO

-- =============================================
-- TABLA DE COMENTARIOS
-- =============================================
CREATE TABLE Comentarios (
    ComentarioID INT IDENTITY(1,1) PRIMARY KEY,
    UsuarioID INT NOT NULL,
    PublicacionID INT NOT NULL,
    Comentario NVARCHAR(500) NOT NULL,
    FechaComentario DATETIME2 DEFAULT GETDATE(),
    Activo BIT DEFAULT 1,
    CONSTRAINT FK_Comentarios_Usuarios FOREIGN KEY (UsuarioID) REFERENCES Usuarios(UsuarioID),
    CONSTRAINT FK_Comentarios_Publicaciones FOREIGN KEY (PublicacionID) REFERENCES Publicaciones(PublicacionID)
);
GO

-- =============================================
-- TABLA DE SEGUIDORES
-- =============================================
CREATE TABLE Seguidores (
    SeguidorID INT IDENTITY(1,1) PRIMARY KEY,
    UsuarioSeguidorID INT NOT NULL,
    UsuarioSeguidoID INT NOT NULL,
    FechaSeguimiento DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_Seguidores_Seguidor FOREIGN KEY (UsuarioSeguidorID) REFERENCES Usuarios(UsuarioID),
    CONSTRAINT FK_Seguidores_Seguido FOREIGN KEY (UsuarioSeguidoID) REFERENCES Usuarios(UsuarioID),
    CONSTRAINT UK_Seguidores UNIQUE (UsuarioSeguidorID, UsuarioSeguidoID),
    CONSTRAINT CK_Seguidores CHECK (UsuarioSeguidorID != UsuarioSeguidoID)
);
GO

-- =============================================
-- TABLA DE NOTIFICACIONES
-- =============================================
CREATE TABLE Notificaciones (
    NotificacionID INT IDENTITY(1,1) PRIMARY KEY,
    UsuarioID INT NOT NULL,
    TipoNotificacion NVARCHAR(50) NOT NULL, -- 'like', 'comentario', 'seguimiento', 'compartido'
    Mensaje NVARCHAR(200) NOT NULL,
    PublicacionID INT NULL,
    UsuarioOrigenID INT NULL,
    Leida BIT DEFAULT 0,
    FechaNotificacion DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_Notificaciones_Usuarios FOREIGN KEY (UsuarioID) REFERENCES Usuarios(UsuarioID),
    CONSTRAINT FK_Notificaciones_Publicaciones FOREIGN KEY (PublicacionID) REFERENCES Publicaciones(PublicacionID),
    CONSTRAINT FK_Notificaciones_UsuarioOrigen FOREIGN KEY (UsuarioOrigenID) REFERENCES Usuarios(UsuarioID)
);
GO

-- =============================================
-- TABLA DE CONFIGURACIONES
-- =============================================
CREATE TABLE Configuraciones (
    ConfiguracionID INT IDENTITY(1,1) PRIMARY KEY,
    Clave NVARCHAR(100) NOT NULL UNIQUE,
    Valor NVARCHAR(500) NOT NULL,
    Descripcion NVARCHAR(200),
    FechaActualizacion DATETIME2 DEFAULT GETDATE()
);
GO

-- =============================================
-- INSERTAR CATEGORÍAS INICIALES
-- =============================================
INSERT INTO Categorias (Nombre, Descripcion, Icono, Color) VALUES
('paisajes', 'Paisajes naturales y urbanos', 'fas fa-mountain', '#10b981'),
('animales', 'Fotografía de vida salvaje y mascotas', 'fas fa-paw', '#f59e0b'),
('arte', 'Arte digital y tradicional', 'fas fa-palette', '#8b5cf6'),
('comida', 'Gastronomía y recetas', 'fas fa-utensils', '#ef4444'),
('arquitectura', 'Diseño y construcción', 'fas fa-building', '#6b7280'),
('moda', 'Estilo y tendencias', 'fas fa-tshirt', '#ec4899'),
('viajes', 'Aventuras y destinos', 'fas fa-plane', '#06b6d4'),
('musica', 'Instrumentos y conciertos', 'fas fa-music', '#84cc16'),
('tecnologia', 'Innovación y gadgets', 'fas fa-laptop', '#3b82f6'),
('fotografia', 'Técnicas y equipos', 'fas fa-camera', '#f97316'),
('naturaleza', 'Flora y fauna', 'fas fa-leaf', '#22c55e'),
('deporte', 'Actividades físicas', 'fas fa-dumbbell', '#eab308');
GO

-- =============================================
-- INSERTAR USUARIOS DE EJEMPLO
-- =============================================
INSERT INTO Usuarios (NombreUsuario, NombreCompleto, Email, Avatar) VALUES
('admin', 'Administrador FocusView', 'admin@focusview.com', 'AD'),
('maria_rodriguez', 'María Rodríguez', 'maria@email.com', 'MR'),
('juan_garcia', 'Juan García', 'juan@email.com', 'JG'),
('ana_lopez', 'Ana López', 'ana@email.com', 'AL'),
('carlos_sanchez', 'Carlos Sánchez', 'carlos@email.com', 'CS'),
('laura_martinez', 'Laura Martínez', 'laura@email.com', 'LM'),
('pedro_hernandez', 'Pedro Hernández', 'pedro@email.com', 'PH'),
('sofia_fernandez', 'Sofía Fernández', 'sofia@email.com', 'SF'),
('diego_ramirez', 'Diego Ramírez', 'diego@email.com', 'DR'),
('valeria_torres', 'Valeria Torres', 'valeria@email.com', 'VT'),
('roberto_castro', 'Roberto Castro', 'roberto@email.com', 'RC');
GO

-- =============================================
-- INSERTAR CONFIGURACIONES INICIALES
-- =============================================
INSERT INTO Configuraciones (Clave, Valor, Descripcion) VALUES
('max_upload_size', '10485760', 'Tamaño máximo de archivo en bytes (10MB)'),
('allowed_formats', 'jpg,jpeg,png,gif', 'Formatos de imagen permitidos'),
('posts_per_page', '20', 'Publicaciones por página'),
('enable_comments', 'true', 'Habilitar comentarios'),
('enable_sharing', 'true', 'Habilitar compartir'),
('maintenance_mode', 'false', 'Modo de mantenimiento');
GO

-- =============================================
-- CREAR ÍNDICES PARA OPTIMIZACIÓN
-- =============================================
CREATE INDEX IX_Publicaciones_UsuarioID ON Publicaciones(UsuarioID);
CREATE INDEX IX_Publicaciones_CategoriaID ON Publicaciones(CategoriaID);
CREATE INDEX IX_Publicaciones_FechaPublicacion ON Publicaciones(FechaPublicacion DESC);
CREATE INDEX IX_Publicaciones_Likes ON Publicaciones(Likes DESC);
CREATE INDEX IX_Likes_PublicacionID ON Likes(PublicacionID);
CREATE INDEX IX_Guardados_UsuarioID ON Guardados(UsuarioID);
CREATE INDEX IX_Comentarios_PublicacionID ON Comentarios(PublicacionID);
CREATE INDEX IX_Notificaciones_UsuarioID ON Notificaciones(UsuarioID, Leida);
GO

-- =============================================
-- PROCEDIMIENTOS ALMACENADOS
-- =============================================

-- Procedimiento para obtener publicaciones por categoría
CREATE PROCEDURE sp_GetPublicacionesPorCategoria
    @CategoriaID INT = NULL,
    @PageNumber INT = 1,
    @PageSize INT = 20
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @Offset INT = (@PageNumber - 1) * @PageSize;
    
    SELECT 
        p.PublicacionID,
        p.Titulo,
        p.Descripcion,
        p.ImagenURL,
        p.Likes,
        p.Vistas,
        p.Guardados,
        p.Compartidos,
        p.FechaPublicacion,
        u.NombreUsuario,
        u.Avatar,
        c.Nombre as CategoriaNombre,
        c.Color as CategoriaColor
    FROM Publicaciones p
    INNER JOIN Usuarios u ON p.UsuarioID = u.UsuarioID
    INNER JOIN Categorias c ON p.CategoriaID = c.CategoriaID
    WHERE p.Activa = 1
    AND (@CategoriaID IS NULL OR p.CategoriaID = @CategoriaID)
    ORDER BY p.FechaPublicacion DESC
    OFFSET @Offset ROWS
    FETCH NEXT @PageSize ROWS ONLY;
END;
GO

-- Procedimiento para dar like a una publicación
CREATE PROCEDURE sp_DarLike
    @UsuarioID INT,
    @PublicacionID INT
AS
BEGIN
    SET NOCOUNT ON;
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Verificar si ya existe el like
        IF NOT EXISTS (SELECT 1 FROM Likes WHERE UsuarioID = @UsuarioID AND PublicacionID = @PublicacionID)
        BEGIN
            -- Insertar like
            INSERT INTO Likes (UsuarioID, PublicacionID) VALUES (@UsuarioID, @PublicacionID);
            
            -- Actualizar contador
            UPDATE Publicaciones 
            SET Likes = Likes + 1 
            WHERE PublicacionID = @PublicacionID;
            
            -- Crear notificación
            DECLARE @Titulo NVARCHAR(200);
            DECLARE @UsuarioOrigen NVARCHAR(50);
            
            SELECT @Titulo = Titulo FROM Publicaciones WHERE PublicacionID = @PublicacionID;
            SELECT @UsuarioOrigen = NombreUsuario FROM Usuarios WHERE UsuarioID = @UsuarioID;
            
            INSERT INTO Notificaciones (UsuarioID, TipoNotificacion, Mensaje, PublicacionID, UsuarioOrigenID)
            SELECT UsuarioID, 'like', @UsuarioOrigen + ' le gustó tu publicación "' + @Titulo + '"', @PublicacionID, @UsuarioID
            FROM Publicaciones WHERE PublicacionID = @PublicacionID AND UsuarioID != @UsuarioID;
            
            SELECT 'Like agregado exitosamente' as Resultado;
        END
        ELSE
        BEGIN
            -- Quitar like
            DELETE FROM Likes WHERE UsuarioID = @UsuarioID AND PublicacionID = @PublicacionID;
            
            -- Actualizar contador
            UPDATE Publicaciones 
            SET Likes = Likes - 1 
            WHERE PublicacionID = @PublicacionID;
            
            SELECT 'Like removido exitosamente' as Resultado;
        END
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
GO

-- Procedimiento para crear una nueva publicación
CREATE PROCEDURE sp_CrearPublicacion
    @UsuarioID INT,
    @Titulo NVARCHAR(200),
    @Descripcion NVARCHAR(500) = NULL,
    @ImagenURL NVARCHAR(500),
    @ImagenNombre NVARCHAR(200) = NULL,
    @ImagenTamaño BIGINT = NULL,
    @CategoriaID INT
AS
BEGIN
    SET NOCOUNT ON;
    
    INSERT INTO Publicaciones (
        UsuarioID, Titulo, Descripcion, ImagenURL, 
        ImagenNombre, ImagenTamaño, CategoriaID
    )
    VALUES (
        @UsuarioID, @Titulo, @Descripcion, @ImagenURL,
        @ImagenNombre, @ImagenTamaño, @CategoriaID
    );
    
    SELECT SCOPE_IDENTITY() as NuevaPublicacionID;
END;
GO

-- =============================================
-- VISTAS ÚTILES
-- =============================================

-- Vista para estadísticas de usuarios
CREATE VIEW vw_EstadisticasUsuarios AS
SELECT 
    u.UsuarioID,
    u.NombreUsuario,
    u.NombreCompleto,
    COUNT(DISTINCT p.PublicacionID) as TotalPublicaciones,
    SUM(p.Likes) as TotalLikes,
    SUM(p.Vistas) as TotalVistas,
    COUNT(DISTINCT s1.UsuarioSeguidoID) as Siguiendo,
    COUNT(DISTINCT s2.UsuarioSeguidorID) as Seguidores
FROM Usuarios u
LEFT JOIN Publicaciones p ON u.UsuarioID = p.UsuarioID AND p.Activa = 1
LEFT JOIN Seguidores s1 ON u.UsuarioID = s1.UsuarioSeguidorID
LEFT JOIN Seguidores s2 ON u.UsuarioID = s2.UsuarioSeguidoID
WHERE u.Activo = 1
GROUP BY u.UsuarioID, u.NombreUsuario, u.NombreCompleto;
GO

-- Vista para publicaciones populares
CREATE VIEW vw_PublicacionesPopulares AS
SELECT TOP 50
    p.PublicacionID,
    p.Titulo,
    p.ImagenURL,
    p.Likes,
    p.Vistas,
    p.FechaPublicacion,
    u.NombreUsuario,
    u.Avatar,
    c.Nombre as CategoriaNombre,
    (p.Likes + p.Vistas + p.Guardados) as PuntuacionTotal
FROM Publicaciones p
INNER JOIN Usuarios u ON p.UsuarioID = u.UsuarioID
INNER JOIN Categorias c ON p.CategoriaID = c.CategoriaID
WHERE p.Activa = 1
ORDER BY PuntuacionTotal DESC, p.FechaPublicacion DESC;
GO

-- =============================================
-- TRIGGERS PARA MANTENER INTEGRIDAD
-- =============================================

-- Trigger para actualizar fecha de actualización
CREATE TRIGGER tr_Publicaciones_Update
ON Publicaciones
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE Publicaciones 
    SET FechaActualizacion = GETDATE() 
    WHERE PublicacionID IN (SELECT PublicacionID FROM inserted);
END;
GO

-- Trigger para limpiar notificaciones antiguas
CREATE TRIGGER tr_Notificaciones_Insert
ON Notificaciones
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Mantener solo las últimas 100 notificaciones por usuario
    DELETE n1 FROM Notificaciones n1
    WHERE n1.UsuarioID IN (SELECT UsuarioID FROM inserted)
    AND n1.NotificacionID NOT IN (
        SELECT TOP 100 NotificacionID 
        FROM Notificaciones n2 
        WHERE n2.UsuarioID = n1.UsuarioID 
        ORDER BY n2.FechaNotificacion DESC
    );
END;
GO

PRINT 'Base de datos FocusView creada exitosamente!';
PRINT 'Tablas, procedimientos almacenados, vistas y triggers configurados.';
PRINT 'Datos iniciales insertados.';

