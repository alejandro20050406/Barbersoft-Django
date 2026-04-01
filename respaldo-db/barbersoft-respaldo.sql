-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: 127.0.0.1    Database: barbersoft
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `categorias_de_productos`
--

DROP TABLE IF EXISTS `categorias_de_productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `categorias_de_productos` (
  `idCategorias_de_Productos` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_categoria` varchar(50) NOT NULL,
  PRIMARY KEY (`idCategorias_de_Productos`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias_de_productos`
--

LOCK TABLES `categorias_de_productos` WRITE;
/*!40000 ALTER TABLE `categorias_de_productos` DISABLE KEYS */;
INSERT INTO `categorias_de_productos` VALUES (1,'Geles y ceras'),(2,'Shampoos'),(3,'Acondicionadores');
/*!40000 ALTER TABLE `categorias_de_productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clientes`
--

DROP TABLE IF EXISTS `clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `clientes` (
  `id_cliente` int(11) NOT NULL AUTO_INCREMENT,
  `apellido_paterno` varchar(50) NOT NULL,
  `apellido_materno` varchar(50) DEFAULT NULL,
  `nombres` varchar(75) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clientes`
--

LOCK TABLES `clientes` WRITE;
/*!40000 ALTER TABLE `clientes` DISABLE KEYS */;
/*!40000 ALTER TABLE `clientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `empleados`
--

DROP TABLE IF EXISTS `empleados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `empleados` (
  `id_empleado` int(11) NOT NULL AUTO_INCREMENT,
  `apellido_paterno` varchar(50) NOT NULL,
  `apellido_materno` varchar(50) DEFAULT NULL,
  `nombres` varchar(75) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `fecha_contratacion` date DEFAULT NULL,
  PRIMARY KEY (`id_empleado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empleados`
--

LOCK TABLES `empleados` WRITE;
/*!40000 ALTER TABLE `empleados` DISABLE KEYS */;
/*!40000 ALTER TABLE `empleados` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `metodos_de_pago`
--

DROP TABLE IF EXISTS `metodos_de_pago`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `metodos_de_pago` (
  `id_metodo_de_pago` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_metodo_pago` varchar(50) NOT NULL,
  PRIMARY KEY (`id_metodo_de_pago`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `metodos_de_pago`
--

LOCK TABLES `metodos_de_pago` WRITE;
/*!40000 ALTER TABLE `metodos_de_pago` DISABLE KEYS */;
INSERT INTO `metodos_de_pago` VALUES (1,'Efectivo'),(2,'Transferencia');
/*!40000 ALTER TABLE `metodos_de_pago` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pagos`
--

DROP TABLE IF EXISTS `pagos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pagos` (
  `id_pago` int(11) NOT NULL AUTO_INCREMENT,
  `fk_id_venta` int(11) NOT NULL,
  `fk_id_metodo_pago` int(11) NOT NULL,
  `monto` float DEFAULT NULL,
  PRIMARY KEY (`id_pago`),
  KEY `fk_id_venta_idx` (`fk_id_venta`),
  KEY `fk_id_metodo_pago_idx` (`fk_id_metodo_pago`),
  CONSTRAINT `fk_id_metodo_pago` FOREIGN KEY (`fk_id_metodo_pago`) REFERENCES `metodos_de_pago` (`id_metodo_de_pago`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_id_venta` FOREIGN KEY (`fk_id_venta`) REFERENCES `ventas` (`id_venta`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pagos`
--

LOCK TABLES `pagos` WRITE;
/*!40000 ALTER TABLE `pagos` DISABLE KEYS */;
/*!40000 ALTER TABLE `pagos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `productos` (
  `id_producto` int(11) NOT NULL AUTO_INCREMENT,
  `fk_id_categoria` int(11) NOT NULL,
  `marca` varchar(30) DEFAULT NULL,
  `modelo` varchar(30) DEFAULT NULL,
  `stock_actual` int(11) DEFAULT NULL,
  `stock_minimo` int(11) DEFAULT NULL,
  `estado` tinyint(1) DEFAULT NULL,
  `precio_compra` float DEFAULT NULL,
  `precio_venta` float DEFAULT NULL,
  PRIMARY KEY (`id_producto`),
  KEY `fk_categorias_de_productos_idx` (`fk_id_categoria`),
  CONSTRAINT `fk_categorias_de_productos` FOREIGN KEY (`fk_id_categoria`) REFERENCES `categorias_de_productos` (`idCategorias_de_Productos`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `servicios`
--

DROP TABLE IF EXISTS `servicios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `servicios` (
  `id_servicio` int(11) NOT NULL,
  `fk_id_tipo_servicio` int(11) NOT NULL,
  `nombre` varchar(45) NOT NULL,
  `precio` float NOT NULL,
  `descripcion` varchar(100) NOT NULL,
  PRIMARY KEY (`id_servicio`),
  UNIQUE KEY `id_servicio_UNIQUE` (`id_servicio`),
  KEY `fk_servicio_tipo_servicio_idx` (`fk_id_tipo_servicio`),
  CONSTRAINT `fk_servicio_tipo_servicio` FOREIGN KEY (`fk_id_tipo_servicio`) REFERENCES `tipos_de_servicios` (`id_tipo_servicio`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `servicios`
--

LOCK TABLES `servicios` WRITE;
/*!40000 ALTER TABLE `servicios` DISABLE KEYS */;
/*!40000 ALTER TABLE `servicios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipos_de_servicios`
--

DROP TABLE IF EXISTS `tipos_de_servicios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tipos_de_servicios` (
  `id_tipo_servicio` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_tipo_servicio` varchar(50) NOT NULL,
  PRIMARY KEY (`id_tipo_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipos_de_servicios`
--

LOCK TABLES `tipos_de_servicios` WRITE;
/*!40000 ALTER TABLE `tipos_de_servicios` DISABLE KEYS */;
INSERT INTO `tipos_de_servicios` VALUES (1,'Corte'),(2,'Barba'),(3,'Corte y Barba'),(4,'Ceja'),(5,'Tinte de barba'),(6,'Mascarilla'),(7,'Corte a tijera'),(8,'Recortes'),(9,'Lavado de Cabello'),(10,'Combo completo'),(11,'Combo Barbón'),(12,'Alaciado'),(13,'Enchinado'),(14,'Extracción de Color'),(15,'Rayitos');
/*!40000 ALTER TABLE `tipos_de_servicios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `venta_detalle_producto`
--

DROP TABLE IF EXISTS `venta_detalle_producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `venta_detalle_producto` (
  `id_venta_detalle_producto` int(11) NOT NULL,
  `fk_id_venta` int(11) NOT NULL,
  `fk_id_producto` int(11) NOT NULL,
  `cantidad` smallint(6) NOT NULL,
  `precio_unitario` float NOT NULL,
  `subtotal_linea` float NOT NULL,
  PRIMARY KEY (`id_venta_detalle_producto`),
  UNIQUE KEY `id_venta_detalle_producto_UNIQUE` (`id_venta_detalle_producto`),
  KEY `fk_vdp_venta_idx` (`fk_id_venta`),
  KEY `fk_vdp_producto_idx` (`fk_id_producto`),
  CONSTRAINT `fk_vdp_producto` FOREIGN KEY (`fk_id_producto`) REFERENCES `productos` (`id_producto`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_vdp_venta` FOREIGN KEY (`fk_id_venta`) REFERENCES `ventas` (`id_venta`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `venta_detalle_producto`
--

LOCK TABLES `venta_detalle_producto` WRITE;
/*!40000 ALTER TABLE `venta_detalle_producto` DISABLE KEYS */;
/*!40000 ALTER TABLE `venta_detalle_producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `venta_detalle_servicio`
--

DROP TABLE IF EXISTS `venta_detalle_servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `venta_detalle_servicio` (
  `id_venta_detalle_servicio` int(11) NOT NULL,
  `fk_id_venta` int(11) NOT NULL,
  `fk_id_servicio` int(11) NOT NULL,
  `cantidad` smallint(6) NOT NULL,
  `precio_unitario` float NOT NULL,
  `subtotal_linea` float NOT NULL,
  PRIMARY KEY (`id_venta_detalle_servicio`),
  UNIQUE KEY `id_venta_detalle_servicio_UNIQUE` (`id_venta_detalle_servicio`),
  KEY `fk_vds_venta_idx` (`fk_id_venta`),
  KEY `fk_vds_servicio_idx` (`fk_id_servicio`),
  CONSTRAINT `fk_vds_servicio` FOREIGN KEY (`fk_id_servicio`) REFERENCES `servicios` (`id_servicio`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_vds_venta` FOREIGN KEY (`fk_id_venta`) REFERENCES `ventas` (`id_venta`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `venta_detalle_servicio`
--

LOCK TABLES `venta_detalle_servicio` WRITE;
/*!40000 ALTER TABLE `venta_detalle_servicio` DISABLE KEYS */;
/*!40000 ALTER TABLE `venta_detalle_servicio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventas`
--

DROP TABLE IF EXISTS `ventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ventas` (
  `id_venta` int(11) NOT NULL AUTO_INCREMENT,
  `fk_id_empleado` int(11) NOT NULL,
  `fk_id_cliente` int(11) NOT NULL,
  `fk_id_metodo_pago` int(11) NOT NULL,
  `fecha` datetime DEFAULT NULL,
  `subtotal` float DEFAULT NULL,
  `total` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_venta`),
  KEY `fk_id_empleado_idx` (`fk_id_empleado`),
  KEY `fk_id_cliente_idx` (`fk_id_cliente`),
  CONSTRAINT `fk_id_cliente` FOREIGN KEY (`fk_id_cliente`) REFERENCES `clientes` (`id_cliente`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_id_empleado` FOREIGN KEY (`fk_id_empleado`) REFERENCES `empleados` (`id_empleado`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas`
--

LOCK TABLES `ventas` WRITE;
/*!40000 ALTER TABLE `ventas` DISABLE KEYS */;
/*!40000 ALTER TABLE `ventas` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-29 12:23:52
