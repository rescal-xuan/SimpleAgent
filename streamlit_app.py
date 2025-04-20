import streamlit as st
import base64  # Import base64 for background image encoding
import os # Import os module for temporary file management

from SimpleAgnet import SimpleAgent

agent = SimpleAgent("Agent007")

# --- Streamlit App ---
st.set_page_config(page_title="Intelligent Agent", page_icon="🤖", layout="wide")

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    .stApp {
      background-image: url("data:image/png;base64,%s");
      background-size: cover;
      background-repeat: no-repeat;
      background-attachment: scroll;
    }
    </style>
    ''' % bin_str

    st.markdown(page_bg_img, unsafe_allow_html=True)

# Set the background image (Replace 'background.png' with your image file)
# Make sure that background.png is on the same folder with your script.
# set_png_as_page_bg('background.png')  # Activate to use a background image
# If you want a solid color you can comment out the set_png_as_page_bg() and leave the styles bellow.

# Custom CSS for a futuristic, cool aesthetic
st.markdown(
    """
    <style>

    /* Titles and Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #64FFDA;  /* Teal color for headings */
        font-family: 'Courier New', monospace;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);  /* Add a subtle shadow */
    }

     /* Add a glow effect to the title */
    .glow {
      font-size: 60px;
      color: #fff;
      text-align: center;
      animation: glow 1s ease-in-out infinite alternate;
    }

    @keyframes glow {
      from {
        text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #e60073, 0 0 40px #e60073, 0 0 50px #e60073, 0 0 60px #e60073, 0 0 70px #e60073;
      }

      to {
        text-shadow: 0 0 20px #fff, 0 0 30px #ff4da6, 0 0 40px #ff4da6, 0 0 50px #ff4da6, 0 0 60px #ff4da6, 0 0 70px #ff4da6, 0 0 80px #ff4da6;
      }
    }


    /* Text Input */
    .stTextInput > label {
        color: #ffffff;
        font-weight: bold;
    }
    .stTextInput > div > div > input {
        background-color: rgba(51, 51, 51, 0.7);  /* Translucent background */
        color: #ffffff;
        border: 1px solid #64FFDA;
        border-radius: 4px;
        padding: 7px; /* Increased padding */
        box-shadow: 0 2px 5px rgba(0, 255, 218, 0.3); /* Add a shadow */
    }

    /* Button */
    .stButton > button {
        background: linear-gradient(to right, #64FFDA, #33CBD8); /* Gradient background */
        color: #000000;
        border: none;
        border-radius: 6px;
        padding: 10px 20px; /* Increased padding */
        cursor: pointer;
        font-weight: bold;
        transition: transform 0.2s;  /* Add a slight scale effect on hover */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); /* Add a stronger shadow */
    }

    .stButton > button:hover {
        transform: scale(1.05); /* Slightly scale the button on hover */
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.5); /* Increase shadow on hover */
    }

    /* File Uploader */
    .stFileUploader label {
        color: #ffffff;
        font-weight: bold;
    }

    .stFileUploader div div div {
        background-color: rgba(51, 51, 51, 0.7);  /* Translucent background */
        border: 1px solid #64FFDA;
        border-radius: 4px;
        color: #ffffff;
    }

     /* Add a glowing effect to the file uploader */
    .stFileUploader label:hover {
      color: #64FFDA;
      text-shadow: 0 0 5px #64FFDA, 0 0 10px #64FFDA;
    }

    /* Chat bubble style */
    .stChatMessage {
        background-color: rgba(68, 68, 68, 0.8); /* Translucent dark background */
        color: #ffffff;
        border-radius: 10px;
        padding: 10px 15px; /* Increased padding */
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.5); /* Add a subtle shadow */
    }

    /* Spinner Color */
    .stSpinner > div > div {
        color: #64FFDA;
    }

    /* Wide layout adjustments */
    .stApp > div.block-container {
        padding-top: 40px;
        padding-bottom: 40px;
    }
     /* Add a subtle border to the container */
    .stApp {
        border: 1px solid rgba(100, 255, 218, 0.3); /* Add a translucent border */
        border-radius: 15px; /* Add a rounded border */
        overflow: hidden; /* Hide any content that overflows the container */
    }

    </style>
    """,
    unsafe_allow_html=True,
)
# Page title (with glow effect)
st.markdown("<h1 style='text-align: center;'>Intelligent Agent 🤖</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Greetings! I am Agent007, ready to assist you.</h3>", unsafe_allow_html=True)




# 用户输入
prompt = st.text_input("Enter your question:", "")

# 文件上传
uploaded_file = st.file_uploader("Upload a document for RAG (PDF)", type=["pdf"])

# 提示信息
if uploaded_file:
    st.info(f"File '{uploaded_file.name}' uploaded successfully.")

# 响应生成
if st.button("Generate Response"):
    with st.spinner("Generating response..."):
        # 添加进度条
        progress_bar = st.progress(0)
        for percent_complete in range(100):
            progress_bar.progress(percent_complete + 1)
        
        if uploaded_file:
            # RAG功能
            file_path = f"{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            response = agent.llm_tool_dispatcher(prompt, file_path)
            os.remove(file_path)  # 处理后清理临时文件
        else:
            # 直接生成响应
            response = agent.llm_tool_dispatcher(prompt)

        # 显示响应在样式化的聊天气泡中
        st.markdown("### Response:")
        with st.container():
            st.markdown(f'<div class="stChatMessage">{response}</div>', unsafe_allow_html=True)