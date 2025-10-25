"""Invoice generator GUI for Agricola Leon Lara SC."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import List

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


@dataclass
class InvoiceItem:
    quantity: Decimal
    description: str
    unit_price: Decimal

    @property
    def total(self) -> Decimal:
        return (self.quantity * self.unit_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class InvoiceApp:
    COMPANY_NAME = "Agrícola León Lara S.C."
    COMPANY_ADDRESS = [
        "CIF: J91305503",
        "C/ Alcade José de la Bandera 15, 1ºC",
        "41003 Sevilla",
        "Sevilla",
        "Tel: 954 000 000",
        "Email: administracion@agricolaleonlara.es",
    ]

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Generador de facturas - Agrícola León Lara S.C.")
        self.items: List[InvoiceItem] = []

        self.invoice_number_var = tk.StringVar(value="1")
        self.invoice_date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        self.customer_name_var = tk.StringVar()
        self.customer_tax_id_var = tk.StringVar()
        self.customer_address_var = tk.StringVar()
        self.customer_city_var = tk.StringVar()
        self.customer_postal_code_var = tk.StringVar()

        self.campaign_var = tk.StringVar()
        self.notes_var = tk.StringVar()

        self.vat_rate_var = tk.StringVar(value="21")
        self.withholding_rate_var = tk.StringVar(value="2")

        self.item_quantity_var = tk.StringVar()
        self.item_description_var = tk.StringVar()
        self.item_unit_price_var = tk.StringVar()

        self._build_interface()
        self.vat_rate_var.trace_add("write", lambda *_: self._update_totals())
        self.withholding_rate_var.trace_add("write", lambda *_: self._update_totals())
        self._update_totals()

    # region GUI construction
    def _build_interface(self) -> None:
        content = ttk.Frame(self.root, padding=15)
        content.grid(column=0, row=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)

        self._build_invoice_meta(content)
        self._build_customer_section(content)
        self._build_items_section(content)
        self._build_totals_section(content)
        self._build_actions(content)

    def _build_invoice_meta(self, parent: ttk.Frame) -> None:
        meta_frame = ttk.LabelFrame(parent, text="Datos de la factura")
        meta_frame.grid(column=0, row=0, columnspan=2, sticky="ew", pady=(0, 10))
        meta_frame.columnconfigure(1, weight=1)

        ttk.Label(meta_frame, text="Número de factura:").grid(column=0, row=0, sticky="w", padx=5, pady=5)
        ttk.Entry(meta_frame, textvariable=self.invoice_number_var).grid(column=1, row=0, sticky="ew", padx=5, pady=5)

        ttk.Label(meta_frame, text="Fecha:").grid(column=2, row=0, sticky="w", padx=5, pady=5)
        ttk.Entry(meta_frame, textvariable=self.invoice_date_var).grid(column=3, row=0, sticky="ew", padx=5, pady=5)

        ttk.Label(meta_frame, text="Campaña / Concepto:").grid(column=0, row=1, sticky="w", padx=5, pady=5)
        ttk.Entry(meta_frame, textvariable=self.campaign_var).grid(column=1, row=1, columnspan=3, sticky="ew", padx=5, pady=5)

    def _build_customer_section(self, parent: ttk.Frame) -> None:
        customer_frame = ttk.LabelFrame(parent, text="Datos del cliente")
        customer_frame.grid(column=0, row=1, columnspan=2, sticky="ew", pady=(0, 10))
        for col in range(4):
            customer_frame.columnconfigure(col, weight=1)

        ttk.Label(customer_frame, text="Nombre / Razón social:").grid(column=0, row=0, sticky="w", padx=5, pady=5)
        ttk.Entry(customer_frame, textvariable=self.customer_name_var).grid(column=1, row=0, columnspan=3, sticky="ew", padx=5, pady=5)

        ttk.Label(customer_frame, text="NIF / CIF:").grid(column=0, row=1, sticky="w", padx=5, pady=5)
        ttk.Entry(customer_frame, textvariable=self.customer_tax_id_var).grid(column=1, row=1, sticky="ew", padx=5, pady=5)

        ttk.Label(customer_frame, text="Dirección:").grid(column=0, row=2, sticky="w", padx=5, pady=5)
        ttk.Entry(customer_frame, textvariable=self.customer_address_var).grid(column=1, row=2, columnspan=3, sticky="ew", padx=5, pady=5)

        ttk.Label(customer_frame, text="Ciudad:").grid(column=0, row=3, sticky="w", padx=5, pady=5)
        ttk.Entry(customer_frame, textvariable=self.customer_city_var).grid(column=1, row=3, sticky="ew", padx=5, pady=5)

        ttk.Label(customer_frame, text="Código postal:").grid(column=2, row=3, sticky="w", padx=5, pady=5)
        ttk.Entry(customer_frame, textvariable=self.customer_postal_code_var).grid(column=3, row=3, sticky="ew", padx=5, pady=5)

        ttk.Label(customer_frame, text="Notas para el pie de factura:").grid(column=0, row=4, sticky="nw", padx=5, pady=5)
        ttk.Entry(customer_frame, textvariable=self.notes_var).grid(column=1, row=4, columnspan=3, sticky="ew", padx=5, pady=5)

    def _build_items_section(self, parent: ttk.Frame) -> None:
        items_frame = ttk.LabelFrame(parent, text="Líneas de factura")
        items_frame.grid(column=0, row=2, columnspan=2, sticky="nsew", pady=(0, 10))
        parent.rowconfigure(2, weight=1)
        items_frame.columnconfigure(0, weight=1)

        form_frame = ttk.Frame(items_frame)
        form_frame.grid(column=0, row=0, sticky="ew", padx=5, pady=5)
        for col in range(3):
            form_frame.columnconfigure(col, weight=1)

        ttk.Label(form_frame, text="Cantidad (kgs, h, etc.):").grid(column=0, row=0, sticky="w", padx=5, pady=2)
        ttk.Entry(form_frame, textvariable=self.item_quantity_var).grid(column=0, row=1, sticky="ew", padx=5, pady=2)

        ttk.Label(form_frame, text="Descripción:").grid(column=1, row=0, sticky="w", padx=5, pady=2)
        ttk.Entry(form_frame, textvariable=self.item_description_var).grid(column=1, row=1, sticky="ew", padx=5, pady=2)

        ttk.Label(form_frame, text="Precio unitario (€):").grid(column=2, row=0, sticky="w", padx=5, pady=2)
        ttk.Entry(form_frame, textvariable=self.item_unit_price_var).grid(column=2, row=1, sticky="ew", padx=5, pady=2)

        button_frame = ttk.Frame(items_frame)
        button_frame.grid(column=0, row=1, sticky="ew", padx=5)
        ttk.Button(button_frame, text="Añadir línea", command=self._add_item).grid(column=0, row=0, padx=5, pady=5, sticky="w")
        ttk.Button(button_frame, text="Eliminar seleccionada", command=self._remove_selected_item).grid(column=1, row=0, padx=5, pady=5, sticky="w")

        columns = ("quantity", "description", "unit_price", "total")
        self.tree = ttk.Treeview(items_frame, columns=columns, show="headings", height=6)
        self.tree.heading("quantity", text="Cantidad")
        self.tree.heading("description", text="Descripción")
        self.tree.heading("unit_price", text="Precio unitario")
        self.tree.heading("total", text="Importe")
        self.tree.column("quantity", width=120, anchor="center")
        self.tree.column("description", width=300, anchor="w")
        self.tree.column("unit_price", width=120, anchor="e")
        self.tree.column("total", width=120, anchor="e")
        self.tree.grid(column=0, row=2, sticky="nsew", padx=5, pady=5)

        scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(column=1, row=2, sticky="ns")
        items_frame.rowconfigure(2, weight=1)

    def _build_totals_section(self, parent: ttk.Frame) -> None:
        totals_frame = ttk.LabelFrame(parent, text="Totales")
        totals_frame.grid(column=0, row=3, sticky="nsew", padx=(0, 10))
        parent.columnconfigure(0, weight=1)
        for col in range(2):
            totals_frame.columnconfigure(col, weight=1)

        ttk.Label(totals_frame, text="Base imponible (€):").grid(column=0, row=0, sticky="w", padx=5, pady=5)
        self.base_amount_label = ttk.Label(totals_frame, text="0,00")
        self.base_amount_label.grid(column=1, row=0, sticky="e", padx=5, pady=5)

        ttk.Label(totals_frame, text="IVA %:").grid(column=0, row=1, sticky="w", padx=5, pady=5)
        vat_entry = ttk.Entry(totals_frame, textvariable=self.vat_rate_var, width=6)
        vat_entry.grid(column=0, row=2, sticky="w", padx=5)
        self.vat_amount_label = ttk.Label(totals_frame, text="0,00")
        self.vat_amount_label.grid(column=1, row=2, sticky="e", padx=5)

        ttk.Label(totals_frame, text="Retención IRPF %:").grid(column=0, row=3, sticky="w", padx=5, pady=5)
        withholding_entry = ttk.Entry(totals_frame, textvariable=self.withholding_rate_var, width=6)
        withholding_entry.grid(column=0, row=4, sticky="w", padx=5)
        self.withholding_amount_label = ttk.Label(totals_frame, text="0,00")
        self.withholding_amount_label.grid(column=1, row=4, sticky="e", padx=5)

        ttk.Label(totals_frame, text="Total factura (€):", font=("TkDefaultFont", 10, "bold")).grid(column=0, row=5, sticky="w", padx=5, pady=5)
        self.total_amount_label = ttk.Label(totals_frame, text="0,00", font=("TkDefaultFont", 10, "bold"))
        self.total_amount_label.grid(column=1, row=5, sticky="e", padx=5, pady=5)

    def _build_actions(self, parent: ttk.Frame) -> None:
        actions_frame = ttk.Frame(parent)
        actions_frame.grid(column=1, row=3, sticky="se")

        ttk.Button(actions_frame, text="Exportar a PDF", command=self._export_pdf).grid(column=0, row=0, padx=5, pady=5)
        ttk.Button(actions_frame, text="Salir", command=self.root.quit).grid(column=1, row=0, padx=5, pady=5)

    # endregion GUI construction

    def _parse_decimal(self, value: str) -> Decimal:
        normalized = value.replace(",", ".").strip()
        if not normalized:
            raise InvalidOperation
        return Decimal(normalized)

    def _add_item(self) -> None:
        try:
            quantity = self._parse_decimal(self.item_quantity_var.get())
            unit_price = self._parse_decimal(self.item_unit_price_var.get())
        except InvalidOperation:
            messagebox.showerror("Dato incorrecto", "Revisa la cantidad y el precio unitario.")
            return

        description = self.item_description_var.get().strip()
        if not description:
            messagebox.showerror("Dato incorrecto", "La descripción no puede estar vacía.")
            return

        item = InvoiceItem(quantity=quantity, description=description, unit_price=unit_price)
        self.items.append(item)
        self.tree.insert("", tk.END, values=(self._format_quantity(quantity), description, self._format_currency(unit_price), self._format_currency(item.total)))

        self.item_quantity_var.set("")
        self.item_description_var.set("")
        self.item_unit_price_var.set("")

        self._update_totals()

    def _remove_selected_item(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Eliminar línea", "Selecciona una línea para eliminarla.")
            return
        for item_id in selected:
            index = self.tree.index(item_id)
            self.tree.delete(item_id)
            del self.items[index]
        self._update_totals()

    def _update_totals(self) -> None:
        base_amount = sum((item.total for item in self.items), Decimal("0"))
        vat_rate = self._safe_rate(self.vat_rate_var.get())
        withholding_rate = self._safe_rate(self.withholding_rate_var.get())

        vat_amount = (base_amount * vat_rate / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        withholding_amount = (base_amount * withholding_rate / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_amount = base_amount + vat_amount - withholding_amount

        self.base_amount_label.config(text=self._format_currency(base_amount))
        self.vat_amount_label.config(text=self._format_currency(vat_amount))
        self.withholding_amount_label.config(text=self._format_currency(withholding_amount))
        self.total_amount_label.config(text=self._format_currency(total_amount))

    def _safe_rate(self, value: str) -> Decimal:
        try:
            return self._parse_decimal(value)
        except InvalidOperation:
            return Decimal("0")

    def _export_pdf(self) -> None:
        if not self.items:
            messagebox.showerror("Factura vacía", "Añade al menos una línea antes de exportar.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivo PDF", "*.pdf")],
            initialfile=f"Factura_{self.invoice_number_var.get()}.pdf",
            title="Guardar factura como"
        )
        if not file_path:
            return

        try:
            self._generate_pdf(Path(file_path))
        except Exception as exc:  # pragma: no cover - GUI usage
            messagebox.showerror("Error al generar PDF", str(exc))
            return

        messagebox.showinfo("Factura creada", "La factura se ha exportado correctamente.")

    # region PDF generation
    def _generate_pdf(self, file_path: Path) -> None:
        pdf = canvas.Canvas(str(file_path), pagesize=A4)
        width, height = A4

        margin = 20 * mm
        x_start = margin
        y_start = height - margin

        # Encabezado
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(x_start, y_start, "FACTURA")

        pdf.setFont("Helvetica", 10)
        y_company = y_start - 20
        pdf.drawString(x_start, y_company, self.COMPANY_NAME)
        y_company -= 12
        for line in self.COMPANY_ADDRESS:
            pdf.drawString(x_start, y_company, line)
            y_company -= 12

        # Datos factura
        x_invoice = width - margin - 200
        y_invoice = y_start - 20
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(x_invoice, y_invoice, f"Nº de factura: {self.invoice_number_var.get()}")
        pdf.drawString(x_invoice, y_invoice - 14, f"Fecha: {self.invoice_date_var.get()}")
        if self.campaign_var.get():
            pdf.drawString(x_invoice, y_invoice - 28, f"Concepto: {self.campaign_var.get()}")

        # Datos cliente
        y_client = y_company - 10
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(x_start, y_client, "Cliente")
        pdf.setFont("Helvetica", 10)
        y_client -= 14
        pdf.drawString(x_start, y_client, self.customer_name_var.get())
        y_client -= 12
        if self.customer_tax_id_var.get():
            pdf.drawString(x_start, y_client, f"NIF/CIF: {self.customer_tax_id_var.get()}")
            y_client -= 12
        if self.customer_address_var.get():
            pdf.drawString(x_start, y_client, self.customer_address_var.get())
            y_client -= 12
        city_line = ", ".join(filter(None, [self.customer_postal_code_var.get(), self.customer_city_var.get()]))
        if city_line:
            pdf.drawString(x_start, y_client, city_line)
            y_client -= 12

        table_top = y_client - 20

        # Tabla
        column_widths = [60 * mm, 70 * mm, 35 * mm, 35 * mm]
        headers = ["Cantidad", "Descripción", "Precio", "Importe"]
        y = self._draw_table_header(pdf, x_start, table_top, column_widths, headers)

        pdf.setFont("Helvetica", 10)
        for item in self.items:
            if y < 100:
                pdf.showPage()
                y = self._draw_table_header(pdf, x_start, height - margin, column_widths, headers)
                pdf.setFont("Helvetica", 10)
            pdf.drawRightString(x_start + column_widths[0] - 5, y, self._format_quantity(item.quantity))
            pdf.drawString(x_start + column_widths[0] + 5, y, item.description)
            pdf.drawRightString(x_start + column_widths[0] + column_widths[1] + column_widths[2] - 5, y, self._format_currency(item.unit_price))
            pdf.drawRightString(x_start + sum(column_widths) - 5, y, self._format_currency(item.total))
            y -= 16

        if y < 120:
            pdf.showPage()
            y = height - margin - 40

        # Totales
        base_amount = sum((item.total for item in self.items), Decimal("0"))
        vat_rate = self._safe_rate(self.vat_rate_var.get())
        withholding_rate = self._safe_rate(self.withholding_rate_var.get())
        vat_amount = (base_amount * vat_rate / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        withholding_amount = (base_amount * withholding_rate / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_amount = base_amount + vat_amount - withholding_amount

        totals_x = x_start + column_widths[0] + column_widths[1]
        totals_y = y - 10
        pdf.setFont("Helvetica", 10)
        pdf.drawString(totals_x, totals_y, "Base imponible:")
        pdf.drawRightString(x_start + sum(column_widths) - 5, totals_y, self._format_currency(base_amount))
        totals_y -= 14

        pdf.drawString(totals_x, totals_y, f"IVA {self._format_rate(vat_rate)}:")
        pdf.drawRightString(x_start + sum(column_widths) - 5, totals_y, self._format_currency(vat_amount))
        totals_y -= 14

        pdf.drawString(totals_x, totals_y, f"Retención {self._format_rate(withholding_rate)}:")
        pdf.drawRightString(x_start + sum(column_widths) - 5, totals_y, self._format_currency(withholding_amount))
        totals_y -= 14

        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(totals_x, totals_y, "Total factura:")
        pdf.drawRightString(x_start + sum(column_widths) - 5, totals_y, self._format_currency(total_amount))

        totals_y -= 30
        if self.notes_var.get():
            pdf.setFont("Helvetica", 9)
            pdf.drawString(x_start, totals_y, self.notes_var.get())

        pdf.showPage()
        pdf.save()

    # endregion PDF generation

    def _draw_table_header(
        self,
        pdf: canvas.Canvas,
        x_start: float,
        y: float,
        column_widths: List[float],
        headers: List[str],
    ) -> float:
        pdf.setFont("Helvetica-Bold", 10)
        pdf.setFillColor(colors.lightgrey)
        pdf.rect(x_start, y - 16, sum(column_widths), 16, fill=1, stroke=0)
        pdf.setFillColor(colors.black)
        pdf.drawString(x_start + 5, y - 12, headers[0])
        pdf.drawString(x_start + column_widths[0] + 5, y - 12, headers[1])
        pdf.drawRightString(x_start + column_widths[0] + column_widths[1] + column_widths[2] - 5, y - 12, headers[2])
        pdf.drawRightString(x_start + sum(column_widths) - 5, y - 12, headers[3])
        return y - 20

    def _format_currency(self, value: Decimal) -> str:
        quantized = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"{quantized:.2f}".replace(".", ",")

    def _format_quantity(self, value: Decimal) -> str:
        quantized = value.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
        text = format(quantized, "f").rstrip("0").rstrip(".")
        if not text:
            text = "0"
        return text.replace(".", ",")

    def _format_rate(self, value: Decimal) -> str:
        quantized = value.quantize(Decimal("0.01"))
        text = format(quantized, "f").rstrip("0").rstrip(".")
        if not text:
            text = "0"
        return f"{text.replace('.', ',')}%"

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = InvoiceApp()
    app.run()


if __name__ == "__main__":
    main()
