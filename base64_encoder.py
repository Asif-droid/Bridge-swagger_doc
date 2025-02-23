import base64
import os
def image_to_base64(image_path,output_folder="base64_outputs"):
    """
    Convert an image to a base64-encoded string.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Base64-encoded string of the image (with MIME header).
    """
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        
        # Get file extension
        os.makedirs(output_folder, exist_ok=True)
        filename = os.path.basename(image_path).split(".")[0]
        ext = image_path.split(".")[-1].lower()
        mime_type = f"data:image/{ext};base64,"
        
        full_base64_string = mime_type + encoded_string

        # Save base64 string to a file
        output_file_path = os.path.join(output_folder, f"{filename}.txt")
        with open(output_file_path, "w") as output_file:
            output_file.write(full_base64_string)

        return output_file_path

    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

# Example usage
base64_string = image_to_base64(".\input\sal_cert1.jpg")
print(base64_string)  # Base64 string of the image
