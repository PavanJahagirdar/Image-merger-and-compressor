import streamlit as st
from PIL import Image
from io import BytesIO
from zipfile import ZipFile
import base64

def merge_images(image1, image2, output_format):
    try:
        width1, height1 = image1.size
        width2, height2 = image2.size
        
        collage_width = width1 + width2
        collage_height = max(height1, height2)
        collage = Image.new('RGB', (collage_width, collage_height))
        
        collage.paste(image1, (0, 0))
        collage.paste(image2, (width1, 0))
        
        output_bytes = BytesIO()
        collage.save(output_bytes, format=output_format.upper())
        output_bytes.seek(0)
        
        return output_bytes
    except Exception as e:
        st.error(f"Error processing images: {e}")
        return None

def process_images(file_pairs, output_format):
    try:
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, 'a') as zip_file:
            for idx, (image1, image2) in enumerate(file_pairs):
                base_name = f"image_{idx+1}_merged.{output_format.lower()}"
                merged_image_bytes = merge_images(image1, image2, output_format)
                if merged_image_bytes:
                    zip_file.writestr(base_name, merged_image_bytes.getvalue())
        
        zip_buffer.seek(0)
        return zip_buffer
    except Exception as e:
        st.error(f"Error processing images: {e}")
        return None

def generate_download_link(zip_buffer, filename="merged_images.zip"):
    b64 = base64.b64encode(zip_buffer.getvalue()).decode()
    href = f'<a href="data:application/zip;base64,{b64}" download="{filename}">Download Merged Images</a>'
    return href

st.title("Image Merger and Compressor")

st.write("Upload pairs of images to merge and download them as a ZIP file.")

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

        output_format = st.selectbox("Output Format:", ["JPEG", "PNG"])

        if st.button("Start Processing"):
            zip_buffer = process_images(file_pairs, output_format)
            if zip_buffer:
                st.markdown(generate_download_link(zip_buffer), unsafe_allow_html=True)
