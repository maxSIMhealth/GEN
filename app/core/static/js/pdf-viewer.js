const fallbackMessage = gettext("This browser does not support inline PDFs. Please download the PDF to view it.");

function pdfViewer (url, id) {
    PDFObject.embed(url, "#pdf-"+id, {fallbackLink: fallbackMessage});
}
