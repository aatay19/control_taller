import os
import tempfile
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from libreria.models import Entrada, Salida
from fpdf import FPDF


@login_required
def entrada_detalle_json(request, id):
    """Devuelve los datos de una entrada en formato JSON para el modal de detalle."""
    entrada = get_object_or_404(Entrada, id=id)
    data = {
        'id': entrada.id,
        'fecha': timezone.localtime(entrada.fecha).strftime('%d/%m/%Y %H:%M'),
        'cliente_nombre': entrada.cliente.nombre,
        'cliente_cedula': entrada.cliente.cedula,
        'cliente_telefono': entrada.cliente.telefono or '-',
        'cliente_direccion': entrada.cliente.direccion or '-',
        'cliente_presente': 'Sí' if entrada.cliente_presente else 'No',
        'maquinas': ", ".join([f"{m.modelo} (Ser: {m.serial})" if m.serial else m.modelo for m in entrada.maquinas.all()]),
        'observaciones': entrada.observaciones,
        'repuestos': [{'nombre': r.nombre, 'valor': str(r.valor)} for r in entrada.repuestos.all()],
        'servicios': [{'nombre': s.nombre, 'valor': str(s.valor)} for s in entrada.servicios.all()],
        'total': str(entrada.total),
        'abono': str(entrada.abono),
        'forma_pago_abono': entrada.get_forma_pago_abono_display() if hasattr(entrada, 'get_forma_pago_abono_display') else '-',
        'tasa_dia': str(entrada.tasa_dia),
        'modalidad_pago_restante': entrada.get_modalidad_pago_restante_display() if hasattr(entrada, 'get_modalidad_pago_restante_display') else '-',
        'abono_extra': str(entrada.abono_extra),
        'forma_pago_abono_extra': entrada.get_forma_pago_abono_extra_display() if hasattr(entrada, 'get_forma_pago_abono_extra_display') else '-',
        'tasa_dia_abono_extra': str(entrada.tasa_dia_abono_extra),
        'total_general': str(entrada.total_general),
        'estado': entrada.get_estado_display(),
        'usuario': entrada.usuario.username if entrada.usuario else '-',
    }
    return JsonResponse(data)


class EntradaPDF(FPDF):
    """PDF personalizado para la entrada del taller."""

    def header(self):
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(31, 41, 55)
        self.cell(0, 12, 'COMPROBANTE DE ENTRADA', align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font('Helvetica', '', 10)
        self.set_text_color(107, 114, 128)
        self.cell(0, 6, 'Taller de Costura - Control de Servicio', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        # Linea separadora
        self.set_draw_color(209, 213, 219)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(156, 163, 175)
        self.cell(0, 10, f'Pagina {self.page_no()}', align='C')

    def add_section_title(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(59, 130, 246)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def add_field(self, label, value, bold_value=False):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(55, 65, 81)
        self.cell(60, 7, f'{label}:', new_x="END")
        self.set_font('Helvetica', 'B' if bold_value else '', 10)
        self.set_text_color(17, 24, 39)
        self.cell(0, 7, str(value), new_x="LMARGIN", new_y="NEXT")


class SalidaPDF(FPDF):
    """PDF personalizado para el comprobante de entrega."""

    def header(self):
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(31, 41, 55)
        self.cell(0, 12, 'COMPROBANTE DE ENTREGA', align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font('Helvetica', '', 10)
        self.set_text_color(107, 114, 128)
        self.cell(0, 6, 'Taller de Costura - Control de Servicio', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.set_draw_color(209, 213, 219)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(156, 163, 175)
        self.cell(0, 10, f'Pagina {self.page_no()}', align='C')

    def add_section_title(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(59, 130, 246)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def add_field(self, label, value, bold_value=False):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(55, 65, 81)
        self.cell(60, 7, f'{label}:', new_x="END")
        self.set_font('Helvetica', 'B' if bold_value else '', 10)
        self.set_text_color(17, 24, 39)
        self.cell(0, 7, str(value), new_x="LMARGIN", new_y="NEXT")


@login_required
def entrada_pdf(request, id):
    """Genera PDF de la entrada, opcionalmente con imagen de talonario adjunta."""
    entrada = get_object_or_404(Entrada, id=id)

    pdf = EntradaPDF()
    pdf.add_page()

    # Numero de entrada y fecha
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(17, 24, 39)
    pdf.cell(95, 7, f'Entrada No. {entrada.id}', new_x="END")
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 7, f'Fecha: {timezone.localtime(entrada.fecha).strftime("%d/%m/%Y %H:%M")}', align='R', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Datos del cliente
    pdf.add_section_title('Datos del Cliente')
    pdf.add_field('Nombre', entrada.cliente.nombre)
    pdf.add_field('Cedula', entrada.cliente.cedula)
    pdf.add_field('Telefono', entrada.cliente.telefono or '-')
    pdf.add_field('Direccion', entrada.cliente.direccion or '-')
    pdf.ln(4)

    # Datos de la maquina
    pdf.add_section_title('Datos de la Maquina')
    maquinas_str = ", ".join([f"{m.modelo} (Ser: {m.serial})" if m.serial else m.modelo for m in entrada.maquinas.all()])
    pdf.add_field('Modelos/Seriales', maquinas_str)
    pdf.add_field('Estado', entrada.get_estado_display())
    pdf.add_field('Cliente Presente', 'Sí' if entrada.cliente_presente else 'No')
    pdf.ln(2)

    # Observaciones
    pdf.add_section_title('Observaciones')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(55, 65, 81)
    pdf.multi_cell(0, 6, entrada.observaciones or '-')
    pdf.ln(4)

    # Repuestos y Servicios Desglosados
    pdf.add_section_title('Desglose Financiero')
    
    total_servicios = 0
    servicios = entrada.servicios.all()
    if servicios:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(0, 6, 'Servicios:', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('Helvetica', '', 10)
        for s in servicios:
            pdf.cell(10, 6, '')
            pdf.cell(120, 6, f"- {s.nombre}")
            pdf.cell(0, 6, f"$ {s.valor}", align='R', new_x="LMARGIN", new_y="NEXT")
            total_servicios += s.valor
        pdf.ln(2)

    total_repuestos = 0
    repuestos = entrada.repuestos.all()
    if repuestos:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(0, 6, 'Repuestos:', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('Helvetica', '', 10)
        for r in repuestos:
            pdf.cell(10, 6, '')
            pdf.cell(120, 6, f"- {r.nombre}")
            pdf.cell(0, 6, f"$ {r.valor}", align='R', new_x="LMARGIN", new_y="NEXT")
            total_repuestos += r.valor
        pdf.ln(2)

    if not servicios and not repuestos:
        pdf.set_font('Helvetica', 'I', 10)
        pdf.cell(0, 6, 'Sin repuestos ni servicios registrados.', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
    else:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(130, 6, 'Subtotal Servicios:')
        pdf.cell(0, 6, f"$ {total_servicios}", align='R', new_x="LMARGIN", new_y="NEXT")
        pdf.cell(130, 6, 'Subtotal Repuestos:')
        pdf.cell(0, 6, f"$ {total_repuestos}", align='R', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    # Linea separadora
    pdf.set_draw_color(229, 231, 235)
    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
    pdf.ln(5)

    pdf.add_field('MONTO TOTAL', f'$ {entrada.total}', bold_value=True)
    forma_pago_str = entrada.get_forma_pago_abono_display() if hasattr(entrada, 'get_forma_pago_abono_display') else '-'
    pdf.add_field('Abono Realizado', f'$ {entrada.abono} ({forma_pago_str})')
    if getattr(entrada, 'abono_extra', 0) > 0:
        forma_pago_extra_str = entrada.get_forma_pago_abono_extra_display() if hasattr(entrada, 'get_forma_pago_abono_extra_display') else '-'
        pdf.add_field('Abono Extra', f'$ {entrada.abono_extra} ({forma_pago_extra_str})')
    pdf.add_field('SALDO PENDIENTE', f'$ {entrada.total_general}', bold_value=True)
    modalidad_str = entrada.get_modalidad_pago_restante_display() if hasattr(entrada, 'get_modalidad_pago_restante_display') else '-'
    pdf.add_field('Modalidad Restante', modalidad_str)
    pdf.add_field('Tasa del Día', f'Bs {entrada.tasa_dia}')
    pdf.ln(4)

    # Registrado por
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(156, 163, 175)
    usuario_nombre = entrada.usuario.username if entrada.usuario else '-'
    pdf.cell(0, 7, f'Registrado por: {usuario_nombre}', new_x="LMARGIN", new_y="NEXT")

    # Imagen del talonario (si fue subida)
    imagen = request.FILES.get('imagen_talonario')
    if imagen:
        # Guardar temporalmente la imagen
        ext = os.path.splitext(imagen.name)[1] or '.jpg'
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            for chunk in imagen.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            pdf.add_page()
            pdf.add_section_title('Imagen del Talonario')
            pdf.ln(4)
            # Insertar imagen centrada, ajustada al ancho de la pagina
            pdf.image(tmp_path, x=25, w=160)
        except Exception:
            pdf.set_font('Helvetica', 'I', 10)
            pdf.set_text_color(220, 38, 38)
            pdf.cell(0, 10, 'Error: No se pudo insertar la imagen del talonario.', new_x="LMARGIN", new_y="NEXT")
        finally:
            os.unlink(tmp_path)

    # Generar respuesta
    pdf_bytes = bytes(pdf.output())
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="entrada_{entrada.id}.pdf"'
    return response


@login_required
def salida_pdf(request, id):
    """Genera PDF del comprobante de entrega/salida."""
    salida = get_object_or_404(Salida, id=id)
    entrada = salida.entrada

    pdf = SalidaPDF()
    pdf.add_page()

    # Encabezado de salida
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(17, 24, 39)
    pdf.cell(95, 7, f'Comprobante de Entrega No. {salida.id}', new_x="END")
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 7, f'Fecha: {timezone.localtime(salida.fecha_entrega).strftime("%d/%m/%Y %H:%M")}', align='R', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Datos del cliente
    pdf.add_section_title('Datos del Cliente')
    pdf.add_field('Nombre', entrada.cliente.nombre)
    pdf.add_field('Cedula', entrada.cliente.cedula)
    pdf.add_field('Telefono', entrada.cliente.telefono or '-')
    pdf.ln(4)

    # Datos de la maquina
    pdf.add_section_title('Equipo Entregado')
    maquinas_str = ", ".join([f"{m.modelo} (Ser: {m.serial})" if m.serial else m.modelo for m in entrada.maquinas.all()])
    pdf.add_field('Modelos/Seriales', maquinas_str or '-')
    pdf.ln(4)

    # Resumen financiero
    pdf.add_section_title('Resumen de Pagos')

    total_servicios = sum(s.valor for s in entrada.servicios.all())
    total_repuestos = sum(r.valor for r in entrada.repuestos.all())

    pdf.add_field('Total Trabajo (Servicios + Repuestos)', f'$ {entrada.total}')

    pdf.set_draw_color(229, 231, 235)
    pdf.line(10, pdf.get_y() + 1, 200, pdf.get_y() + 1)
    pdf.ln(4)

    forma_pago_abono = entrada.get_forma_pago_abono_display() if hasattr(entrada, 'get_forma_pago_abono_display') else '-'
    pdf.add_field('Abono Inicial', f'$ {entrada.abono} ({forma_pago_abono}) - Tasa: Bs {entrada.tasa_dia}')

    if entrada.abono_extra > 0:
        forma_pago_extra = entrada.get_forma_pago_abono_extra_display() if hasattr(entrada, 'get_forma_pago_abono_extra_display') else '-'
        pdf.add_field('Abono Extra', f'$ {entrada.abono_extra} ({forma_pago_extra}) - Tasa: Bs {entrada.tasa_dia_abono_extra}')
        if getattr(entrada, 'observacion_abono_extra', None):
            pdf.set_font('Helvetica', 'I', 9)
            pdf.set_text_color(107, 114, 128)
            pdf.multi_cell(0, 5, f'  Obs: {entrada.observacion_abono_extra}')

    forma_pago_salida = salida.get_forma_pago_salida_display() if hasattr(salida, 'get_forma_pago_salida_display') else '-'
    pdf.add_field('Pago Final', f'$ {salida.pago_final} ({forma_pago_salida}) - Tasa: Bs {salida.tasa_dia_salida}')

    pdf.ln(3)
    pdf.set_draw_color(34, 197, 94)
    pdf.set_line_width(0.8)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(21, 128, 61)
    total_cobrado = entrada.abono + entrada.abono_extra + salida.pago_final
    pdf.cell(0, 8, f'TOTAL COBRADO: $ {total_cobrado}', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Observaciones de entrega
    if salida.observaciones_entrega:
        pdf.add_section_title('Observaciones de Entrega')
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(55, 65, 81)
        pdf.multi_cell(0, 6, salida.observaciones_entrega)
        pdf.ln(4)

    # Garantia
    if salida.garantia:
        pdf.add_section_title('Garantia')
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(55, 65, 81)
        pdf.multi_cell(0, 6, salida.garantia)
        pdf.ln(4)

    # Pie de página informativo
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(156, 163, 175)
    usuario_nombre = salida.usuario.username if salida.usuario else '-'
    pdf.cell(0, 7, f'Entregado por: {usuario_nombre}  |  Entrada No. {entrada.id}', new_x="LMARGIN", new_y="NEXT")

    pdf_bytes = bytes(pdf.output())
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="salida_{salida.id}.pdf"'
    return response
