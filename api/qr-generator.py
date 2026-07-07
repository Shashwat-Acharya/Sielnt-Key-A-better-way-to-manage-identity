import segno


def generate_qr_code(data, filename):
	"""Generate a QR code image for the provided payload."""
	qr = segno.make(data, micro=False)
	qr.save(filename, scale=8, border=2)
	return filename
