import barcode
from barcode.writer import ImageWriter
import cv2
from pyzbar.pyzbar import decode
import os

def generate_barcode(data, filename):
    EAN = barcode.get_barcode_class('ean13')
    ean = EAN(data, writer=ImageWriter())
    if not os.path.exists('barcodes'):
        os.makedirs('barcodes')
    fullname = ean.save(filename)  # Saves the barcode as an image
    return fullname

def read_barcodes():
    cap = cv2.VideoCapture(0)  # Start the webcam
    if not os.path.exists('scanned_barcodes'):
        os.makedirs('scanned_barcodes')
    try:
        while True:
            ret, frame = cap.read()  # Read frames from the webcam
            decoded_objects = decode(frame)
            for obj in decoded_objects:
                print('Detected barcode:', obj.data.decode('utf-8'))  # Print decoded barcode data
                # Display barcode bounding box and data on the image
                cv2.rectangle(frame, (obj.rect.left, obj.rect.top), (obj.rect.width + obj.rect.left, obj.rect.height + obj.rect.top), (0, 255, 0), 2)
                cv2.putText(frame, obj.data.decode('utf-8'), (obj.rect.left, obj.rect.top), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.imwrite(f"scanned_barcodes/{obj.data.decode('utf-8')}.png", frame)  # Save image

            cv2.imshow("Barcode Scanner", frame)
            if cv2.waitKey(1) & 0xFF == 27:  # Exit on ESC
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

def print_barcode(barcode_number):
    filename = f"barcodes/{barcode_number}.png"
    if os.path.exists(filename):
        os.system(f"start {filename}")  # This will open the image with the default image viewer
    else:
        messagebox.showerror("Error", f"Barcode image for {barcode_number} does not exist.")
