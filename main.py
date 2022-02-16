import qrcode
data = "huy"
filename = "site.png"
img = qrcode.make(data)
img.save(filename)