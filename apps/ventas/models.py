from django.db import models
from django.core.exceptions import ValidationError

class Venta(models.Model):
    empleado=models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.PROTECT, 
        related_name='ventas', 
        verbose_name='Empleado'
    )
    cliente=models.ForeignKey(
        'clientes.Cliente', 
        on_delete=models.PROTECT, 
        related_name='ventas', 
        verbose_name='Cliente'
    )
    metodo_de_pago=models.ForeignKey( 
        'catalogos.MetodoDePago',
        on_delete=models.PROTECT,
        related_name='ventas',
        verbose_name='Método de Pago'
    )
    fecha=models.DateField(verbose_name='Fecha de venta')
    total=models.DecimalField( 
        max_digits=10,
        decimal_places=2,
        verbose_name='Total de la venta'
    )

    class Meta:
        db_table = 'ventas'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha']

    def __str__(self):   
        return f'Venta #{self.pk} — {self.fecha}' 
    
class VentaDetalleProducto(models.Model):
    venta=models.ForeignKey(
        Venta, 
        on_delete=models.CASCADE, 
        related_name='detalles_productos', 
        verbose_name='Venta'
    )  
    producto=models.ForeignKey(
        'catalogos.Producto', 
        on_delete=models.PROTECT, 
        related_name='detalles_venta',
        verbose_name='Producto'
    )  
    cantidad=models.PositiveIntegerField(verbose_name='Cantidad')
    precio_unitario=models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Precio Unitario'
    )
    subtotal=models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Subtotal'
    )
    class Meta: 
        db_table='venta_detalle_producto'
        verbose_name='Detalle de producto'
        verbose_name_plural='Detalles de productos'

    def __str__(self):
        return f'Detalle producto #{self.pk} — Venta #{self.venta_id}'   
    
class VentaDetalleServicio(models.Model): 
    venta=models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='detalles_servicio', 
        verbose_name='Venta'        
    )
    servicio=models.ForeignKey(
        'catalogos.Servicio', 
        on_delete=models.PROTECT,
        related_name='detalles_venta',
        verbose_name='Servicio' 
     )
    precio_unitario=models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Precio unitario'
    )
    subtotal=models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Subtotal' 
    )
    
    class Meta: 
        db_table='venta_detalle_servicio'
        verbose_name='Detalle de servicio'
        verbose_name_plural='Detalles de servicios'
    def __str__(self):
        return f'Detalle servicio #{self.pk} — Venta #{self.venta_id}'
    
class Pago(models.Model):
    venta=models.ForeignKey( 
        Venta,
        on_delete=models.CASCADE,
        related_name='pagos',
        verbose_name='Venta'
    )
    metodo_de_pago=models.ForeignKey(
        'catalogos.MetodoDePago',
        on_delete=models.PROTECT,
        related_name='pagos',
        verbose_name='Método de pago'
    )
    monto=models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Monto pagado'
    )
    fecha=models.DateField(verbose_name='Fecha de pago')
    class Meta:
        db_table='pagos'
        verbose_name='Pago'
        verbose_name_plural='Pagos'

    def __str__(self):
         return f'Pago #{self.pk} — Venta #{self.venta_id}' 

class Visita(models.Model):
    cliente=models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.PROTECT, 
        related_name='visitas',
        verbose_name='Cliente'
    )  
    empleado=models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.PROTECT,
        related_name='visitas', 
        verbose_name='Empleado'
    )
    venta=models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='visitas',
        verbose_name='Venta asociada'
    )
    fecha=models.DateField(verbose_name='Fecha de visita') 
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )
    class Meta:
        db_table='visitas'
        verbose_name='Visita'
        verbose_name_plural='Visitas'
        ordering=['-fecha']
    def __str__(self):
         return f'Visita #{self.pk} — Cliente {self.cliente_id}'   

class Comision(models.Model):
    empleado=models.ForeignKey(
        'empleados.Empleado',
        on_delete=models.PROTECT,
        related_name='comisiones',
        verbose_name='Empleado'
    )
    venta=models.ForeignKey(
        Venta,
        on_delete=models.PROTECT,
        related_name='comisiones',
        verbose_name='Venta'
    )
    venta_detalle_producto=models.ForeignKey(
        VentaDetalleProducto,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='comisiones',
        verbose_name='Detalle de producto'
    )
    venta_detalle_servicio=models.ForeignKey(
        VentaDetalleServicio,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='comisiones',
        verbose_name='Detalle de servicio'
    )
    porcentaje=models.DecimalField(
        max_digits=5,
        decimal_places=2, 
        verbose_name='Porcentaje (%)'
    )
    monto=models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Monto de la comisión'
    )
    fecha = models.DateField(verbose_name='Fecha de comisión')
    class Meta:
        db_table = 'comisiones'
        verbose_name = 'Comisión'
        verbose_name_plural = 'Comisiones'

    def clean(self):
        tiene_producto = self.venta_detalle_producto_id is not None
        tiene_servicio = self.venta_detalle_servicio_id is not None

        if not tiene_producto and not tiene_servicio:
            raise ValidationError(
                'Una comisión debe estar asociada a un detalle de '
                'producto o a un detalle de servicio.'
            )
        if tiene_producto and tiene_servicio:
            raise ValidationError(
                'Una comisión no puede estar asociada simultáneamente '
                'a un detalle de producto y a un detalle de servicio.'
            )

    def __str__(self):
        return f'Comisión #{self.pk} — Empleado {self.empleado_id}'  
           



           
