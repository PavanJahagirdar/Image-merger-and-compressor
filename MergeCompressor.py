import streamlit as st
from PIL import Image
from io import BytesIO
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

def compress_image(image_bytes, output_format):
    img = Image.open(image_bytes)
    output_bytes = BytesIO()
    quality = 85

    # Resize to ensure the image fits within an 800x800 bounding box
    max_dimension = 800
    img.thumbnail((max_dimension, max_dimension), Image.ANTIALIAS)

    while True:
        output_bytes = BytesIO()
        img.save(output_bytes, format=output_format.upper(), quality=quality)
        size_kb = output_bytes.tell() / 1024
        if size_kb <= 100:
            break
        quality -= 5
        if quality < 10:
            break

    output_bytes.seek(0)
    return output_bytes

def generate_download_link(file_bytes, filename):
    b64 = base64.b64encode(file_bytes.getvalue()).decode()
    href = f'<a href="data:file/{filename.split(".")[-1]};base64,{b64}" download="{filename}">Download {filename}</a>'
    return href

st.title("Image Merger and Compressor")

st.write("Upload pairs of images to merge and download them in the selected format.")

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

        if output_format:
            st.write("Processing images...")
            for idx, (image1, image2) in enumerate(file_pairs):
                merged_image_bytes = merge_images(image1, image2, output_format)
                if merged_image_bytes:
                    compressed_image_bytes = compress_image(merged_image_bytes, output_format)
                    filename = f"image_{idx+1}_merged.{output_format.lower()}"
                    download_link = generate_download_link(compressed_image_bytes, filename)
                    st.markdown(download_link, unsafe_allow_html=True)
