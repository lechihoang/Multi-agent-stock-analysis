import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'

export interface PDFExportOptions {
  filename?: string
  margin?: number
  format?: 'a4' | 'letter'
}

export async function exportToPDF(
  element: HTMLElement,
  options: PDFExportOptions = {}
): Promise<void> {
  const {
    filename = 'research_report.pdf',
    margin = 10,
    format = 'a4',
  } = options

  const canvas = await html2canvas(element, {
    scale: 2,
    useCORS: true,
    logging: false,
  })

  const imgWidth = 210 - margin * 2
  const pageHeight = 297 - margin * 2
  const imgHeight = (canvas.height * imgWidth) / canvas.width

  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format,
  })

  let heightLeft = imgHeight
  let position = margin

  pdf.addImage(
    canvas.toDataURL('image/png'),
    'PNG',
    margin,
    position,
    imgWidth,
    imgHeight
  )

  heightLeft -= pageHeight

  while (heightLeft > 0) {
    position = heightLeft - imgHeight + margin
    pdf.addPage()
    pdf.addImage(
      canvas.toDataURL('image/png'),
      'PNG',
      margin,
      position,
      imgWidth,
      imgHeight
    )
    heightLeft -= pageHeight
  }

  pdf.save(filename)
}

export function downloadMarkdownReport(content: string, ticker: string): void {
  const filename = ticker ? `${ticker}_research_report.md` : 'research_report.md'
  const blob = new Blob([content], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
