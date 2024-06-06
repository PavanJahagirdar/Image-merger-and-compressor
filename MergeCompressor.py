#!/usr/bin/env python
# coding: utf-8

# In[14]:


import os
import streamlit as st
from PIL import Image
import imageio
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter


# In[15]:


def merge_images(image1_path, image2_path, output_path, output_format):
    try:
        image1 = Image.open(image1_path)
        image2 = Image.open(image2_path)
        width1, height1 = image1.size
        width2, height2 = image2.size
        collage_width = width1 + width2
        collage_height = max(height1, height2)
        collage = Image.new('RGB', (collage_width, collage_height))
        collage.paste(image1, (0, 0))
        collage.paste(image2, (width1, 0))
        if output_format.lower() == 'pdf':
            temp_image_path = output_path.replace('.pdf', '.jpg')
            collage.save(temp_image_path, format='JPEG', quality=50)
            return temp_image_path
        else:
            collage.save(output_path, format=output_format.upper())
            if output_format.lower() in ['jpeg', 'jpg']:
                compress_image(output_path, 100)
        return output_path
    except Exception as e:
        st.error(f"Error processing images {image1_path} and {image2_path}: {e}")
def compress_image(image_path, target_size_kb):
    try:
        img = imageio.imread(image_path)
        quality = 95
        while True:
            imageio.imwrite(image_path, img, format='jpeg', quality=quality)
            if os.path.getsize(image_path) <= target_size_kb * 1024:
                break
            quality -= 5
            if quality < 10:
                break
    except Exception as e:
        st.error(f"Error compressing image {image_path}: {e}")
def create_pdf(output_folder, base_name, collage_image_path):
    try:
        pdf_path = os.path.join(output_folder, f'{base_name}_ab.pdf')
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.drawImage(collage_image_path, 0, 0, width=letter[0], height=letter[1], preserveAspectRatio=True)
        c.save()
        os.remove(collage_image_path)
        compress_pdf(pdf_path, 100)
        return pdf_path
    except Exception as e:
        st.error(f"Error creating PDF {pdf_path}: {e}")
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
        st.error(f"Error compressing PDF {pdf_path}: {e}")
def process_images(input_folder, output_folder, output_format):
    try:
        image_pairs = {}
        valid_extensions = ('.png', '.jpg', '.jpeg')
        for file_name in os.listdir(input_folder):
            if file_name.lower().endswith(valid_extensions):
                base_name = '_'.join(file_name.split('_')[:-1])
                suffix = file_name.split('_')[-1].split('.')[0]
                if base_name not in image_pairs:
                    image_pairs[base_name] = {}
                if suffix in ['a', 'b']:
                    image_pairs[base_name][suffix] = file_name
        for base_name, pair in image_pairs.items():
            if 'a' in pair and 'b' in pair:
                image1_path = os.path.join(input_folder, pair['a'])
                image2_path = os.path.join(input_folder, pair['b'])
                if output_format.lower() == 'pdf':
                    temp_image_path = os.path.join(output_folder, f'{base_name}_ab_temp.jpg')
                    merged_image_path = merge_images(image1_path, image2_path, temp_image_path, 'JPEG')
                    create_pdf(output_folder, base_name, merged_image_path)
                else:
                    output_image_path = os.path.join(output_folder, f'{base_name}_ab.{output_format.lower()}')
                    merge_images(image1_path, image2_path, output_image_path, output_format)
            else:
                st.warning(f"Skipping incomplete pair: {base_name}")
    except Exception as e:
        st.error(f"Error processing images in folder {input_folder}: {e}")
st.title("Image Merger and Compressor")
st.write("Upload a folder containing pairs of images to merge and compress them.")
input_folder = st.text_input("Input Folder Path:")
output_folder = st.text_input("Output Folder Path:")
output_format = st.selectbox("Output Format:", ["JPEG", "PNG", "PDF"])
if st.button("Start Processing"):
    if input_folder and output_folder:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        process_images(input_folder, output_folder, output_format)
        st.success("Images have been processed successfully.")
    else:
        st.warning("Please provide both input and output folder paths.")


# In[ ]:





# In[ ]:




