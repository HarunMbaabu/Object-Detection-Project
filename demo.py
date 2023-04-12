import streamlit as st
from streamlit_chat import message
import openai
from config import open_api_key
openai.api_key = open_api_key
import torch
import detect
from PIL import Image
from io import *
import glob
from datetime import datetime
import os
import wget
import time

# openAI code

# openAI code


def openai_create(prompt):

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"]
    )

    return response.choices[0].text


def chatgpt_clone(input, history):
    history = history or []
    s = list(sum(history, ()))
    print(s)
    s.append(input)
    inp = ' '.join(s)
    output = openai_create(inp)
    history.append((input, output))
    return history, history


def imageInput(device, src):
    if src == 'Upload your own data.':
        image_file = st.file_uploader("Upload An Image", type=['png', 'jpeg', 'jpg'])
        col1, col2 = st.columns(2)
        if image_file is not None:
            img = Image.open(image_file)
            with col1:
                st.image(img, caption='Uploaded Image', use_column_width='always')
            ts = datetime.timestamp(datetime.now())
            imgpath = os.path.join(' ', str(ts) + image_file.name)
            outputpath = os.path.join('data/outputs', os.path.basename(imgpath))
            with open(imgpath, mode="wb") as f:
                f.write(image_file.getbuffer())

            # call Model prediction--
           
            model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt', force_reload=True)
            model.cuda() if device == 'cuda' else model.cpu()
            pred = model(imgpath)
            pred.render()  # render bbox in image
            for im in pred.ims:
                im_base64 = Image.fromarray(im)
                im_base64.save(outputpath)

            # --Display predicton

            img_ = Image.open(outputpath)
            with col2:
                st.image(img_, caption='Model Prediction(s)', use_column_width='always')

    elif src == 'From test set.':
        # Image selector slider
        test_images = os.listdir('data/images/')
        test_image = st.selectbox('Please select a test image:', test_images)
        image_file = 'data/images/' + test_image
        submit = st.button("Predict!")
        col1, col2 = st.columns(2)
        with col1:
            img = Image.open(image_file)
            st.image(img, caption='Selected Image', use_column_width='always')
        with col2:
            if image_file is not None and submit:
                # call Model prediction--
                model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt', force_reload=True)
                pred = model(image_file)
                pred.render()  # render bbox in image
                for im in pred.ims:
                    im_base64 = Image.fromarray(im)
                    im_base64.save(os.path.join('data/outputs', os.path.basename(image_file)))
                    # --Display predicton
                    img_ = Image.open(os.path.join('data/outputs', os.path.basename(image_file)))
                    st.image(img_, caption='Model Prediction(s)')



# Streamlit App
def main():
    # -- Sidebar
    st.sidebar.title('⚙️Options')
    datasrc = st.sidebar.radio("Select input source.", ['From test set.', 'Upload your own data.'])

    # option = st.sidebar.radio("Select input type.", ['Image', 'Video'])
    if torch.cuda.is_available():
        deviceoption = st.sidebar.radio("Select compute Device.", ['cpu', 'cuda'], index=1)
    else:
        deviceoption = st.sidebar.radio("Select compute Device.", ['cpu', 'cuda'], index=0)
    # -- End of Sidebar

    st.header('Fruits 🍎🍊🍌🥕Object Detection Model')
    st.subheader('👈🏽Select the options')
    #st.sidebar.markdown("https://bit.ly/3uvYQ3R")

    imageInput(deviceoption, datasrc)

    st.header("ASK Questions about Kenyan Meals Below;")

    history_input = []

    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []


    def get_text():
        input_text = st.text_input("You: ", key="input")
        return input_text


    user_input = get_text()


    if user_input:
        output = chatgpt_clone(user_input, history_input)
        history_input.append([user_input, output])
        st.session_state.past.append(user_input)
        st.session_state.generated.append(output[0])

    if st.session_state['generated']:

        for i in range(len(st.session_state['generated'])-1, -1, -1):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state['past'][i],
                    is_user=True, key=str(i) + '_user')

if __name__ == '__main__':
    main()