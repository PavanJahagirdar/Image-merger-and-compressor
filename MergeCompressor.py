import os
import streamlit as st
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO

def merge_images(image1, image2, output_path, output_format):
    try:
        width1, height1 = image1.size
        width2, height2 = image2.size
        
        collage_width = width1 + width2
        collage_height = max(height1, height2)
        collage = Image.new('RGB', (collage_width, collage_height))
        
        collage.paste(image1, (0, 0))
        collage.paste(image2, (width1, 0))
        
        if output_format.lower() == 'pdf':
            temp_image = BytesIO()
            collage.save(temp_image, format='JPEG', quality=50)
            temp_image.seek(0)
            return temp_image
        else:
            collage.save(output_path, format=output_format.upper())
            if output_format.lower() in ['jpeg', 'jpg']:
                compress_image(output_path, 100)
        
        return output_path
    except Exception as e:
        st.error(f"Error processing images: {e}")

def compress_image(image_path, target_size_kb):
    try:
        img = Image.open(image_path)
        
        quality = 95
        while True:
            img.save(image_path, 'JPEG', quality=quality)
            if os.path.getsize(image_path) <= target_size_kb * 1024:
                break
            quality -= 5
            if quality < 10:
                break
    except Exception as e:
        st.error(f"Error compressing image: {e}")

def create_pdf(output_folder, base_name, collage_image):
    try:
        pdf_path = os.path.join(output_folder, f'{base_name}_merged.pdf')
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.drawImage(collage_image, 0, 0, width=letter[0], height=letter[1], preserveAspectRatio=True)
        c.save()
        compress_pdf(pdf_path, 100)
        return pdf_path
    except Exception as e:
        st.error(f"Error creating PDF: {e}")

def compress_pdf(pdf_path, target_size_kb):
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        compressed_pdf_path = pdf_path.replace(".pdf", "_compressed.pdf")
        with open(compressed_pdf_path, 'wb') as f:
            writer.write(f)

        if os.path.getsize(compressed_pdf_path) <= target_size_kb * 1024:
            os.replace(compressed_pdf_path, pdf_path)
        else:
            st.warning(f"Compressed PDF size is still above {target_size_kb} KB.")
            os.remove(compressed_pdf_path)
    except Exception as e:
        st.error(f"Error compressing PDF: {e}")

def process_images(file_pairs, output_folder, output_format):
    try:
        for idx, (image1, image2) in enumerate(file_pairs):
            base_name = f"image_{idx+1}"
            if output_format.lower() == 'pdf':
                temp_image = merge_images(image1, image2, None, 'JPEG')
                create_pdf(output_folder, base_name, temp_image)
            else:
                output_image_path = os.path.join(output_folder, f'{base_name}_merged.{output_format.lower()}')
                st.write(f"Saving file to: {output_image_path}")
                merge_images(image1, image2, output_image_path, output_format)
        st.success("Images have been processed successfully.")
    except Exception as e:
        st.error(f"Error processing images: {e}")

st.title("Image Merger and Compressor")

st.write("Upload pairs of images to merge and compress them.")

uploaded_files = st.file_uploader("Choose image files", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

if uploaded_files:
    if len(uploaded_files) % 2 != 0:
        st.warning("Please upload an even number of images to form pairs.")
    else:
        file_pairs = []
        for i in range(0, len(uploaded_files), 2):
            image1 = Image.open(uploaded_files[i])
            image2 = Image.open(uploaded_files[i + 1])
            file_pairs.append((image1, image2))

        output_folder = st.text_input("Output Folder Path:")
        output_format = st.selectbox("Output Format:", ["JPEG", "PNG", "PDF"])

        if st.button("Start Processing"):
            if output_folder:
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                st.write(f"Output folder: {output_folder}")
                process_images(file_pairs, output_folder, output_format)
            else:
                st.warning("Please provide an output folder path.")
