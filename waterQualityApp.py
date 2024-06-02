import gradio as gr
from io import StringIO
import pandas as pd
import joblib
import os
import time

model = joblib.load('C:/Users/etoth/Desktop/model/model3.joblib')

def predict(ph, iron, nitrate, chloride, lead, zinc, 
                                    turbidity, fluoride, copper, odor, sulfate, 
                                    conductivity, chlorine, manganese, tds, water_temp,
                                    color, air_temp, day, source, month, hour, minute):
    

    hour += minute / 60

    water_temp = (water_temp * 9/5) + 32
    air_temp = (air_temp * 9/5) + 32

    Time_of_day = round(hour)

    data = {'pH': [ph], 'Iron': [iron], 'Nitrate': [nitrate], 'Chloride': [chloride], 'Lead': [lead],
            'Zinc': [zinc], 'Turbidity': [turbidity], 'Fluoride': [fluoride], 'Copper': [copper], 'Odor': [odor],
            'Sulfate': [sulfate], 'Conductivity': [conductivity], 'Chlorine': [chlorine], 'Manganese': [manganese], 'Total Dissolved Solids': [tds],
            'Water Temperature': [water_temp], 'Air Temperature': [air_temp], 'Day': [day], 'Time of Day': [Time_of_day], 'ColorInd': [color_mappings[color]],
            'MonthInd': [month_mappings[month]], 'SourceInd': [source_mappings[source]]
            }

    df = pd.DataFrame(data)    
    
    start_time=time.time()
    
    predictions = model.predict(df)

    end_time=time.time()

    result_time = end_time - start_time

    water_class_map={0: "Your water is of poor quality, you should not use it",
                     1: "Your water is safe to DRINK, Congratulations!"}
    
    print("Your time of prediction is " + str(result_time))

    if predictions[0] == 0:
        return '<span style="color: red;">' + water_class_map[0] + '</span>'
    else:
        return '<span style="color: green;">' + water_class_map[1] + '</span>'


def predict_from_file(csv_string):
    
    df = pd.read_csv(csv_string, sep=';')
    columns_to_fill = ['Color', 'Month', 'Source']
    df[columns_to_fill] = df[columns_to_fill].fillna('NA')
    pd.set_option('display.max_columns', None)
    df['ColorInd'] = df['Color'].map(color_mappings)
    df['MonthInd'] = df['Month'].map(month_mappings)
    df['SourceInd'] = df['Source'].map(source_mappings)
    df.drop(['Color', 'Source', 'Month'], axis=1, inplace=True)

    start_time=time.time()

    predictions = model.predict(df)
    df['Predicted_Class'] = predictions

    df.to_csv('predictions.csv', index=False)

    end_time=time.time()
    result_time = end_time - start_time
    print("Your time of prediction for big file is " + str(result_time))

    return 'predictions.csv'


def load_instructions():
    file_path='C:/Users/etoth/Desktop/model/instr.html'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            instructions = file.read()
    else:
        instructions = "Файл с инструкциями не найден"

    return instructions    


months_days = {
    "NA": 31,
    "January": 31,
    "February": 29,
    "March": 31,
    "April": 30,
    "May": 31,
    "June": 30,
    "July": 31,
    "August": 31,
    "September": 30,
    "October": 31,
    "November": 30,
    "December": 31
}

color_mappings = {
    "Colorless": 0,
    "Faint Yellow": 1,
    "Light Yellow": 2,
    "Near Colorless": 3,
    "Yellow": 4,
    "NA": 5
}

month_mappings = {
    "January": 0,
    "November": 1,
    "April": 2,
    "June": 3,
    "March": 4,
    "September": 5,
    "May": 6,
    "July": 7,
    "August": 8,
    "October": 9,
    "December": 10,
    "February": 11,
    "NA": 12
}

source_mappings = {
    "NA": 0,
    "Lake": 1,
    "River": 2,
    "Ground": 3,
    "Spring": 4,
    "Stream": 5,
    "Aquifer": 6,
    "Reservoir": 7,
    "Well": 8
}


examples_good_dict = {0: 
                [
    7.66, 125.4, 3.5, 1.4, 0.4, 0, 0, 0, 8.3, 162, 0.17, 3.9, "Near Colorless", 457, 1.1, 26.5, 0.9, 28, 
    "Spring", "January", 5, 19, 0
],
1: [
    7, 200, 0, 20, 0.8, 0, 0, 0, 30, 0, 0, 0, "Colorless", 0, 0, 50, 0, 0, 
    "River", "April", 1, 0, 0
],
2: [
    8, 267, 3.84, 20, 0.4, 0.28, 0, 1.5, 5.1, 134, 3.7, 12.44, "Light Yellow", 422, 1.8, 363, 0.31, 4.5, 
    "Reservoir", "October", 9, 15, 30
]
}

examples_bad_dict = {0: [
    7.1, 157, 2.28, 0.39, 0.84, 0.003, 0, 0, 3.62, 167, 0.11, 11, "Colorless", 583, 2.71, 113, 0.05, 10, 
    "River", "April", 7, 12, 10
],
1: [
    8.23, 143, 3.79, 0.97, 0.3, 0, 0, 0.03, 3.1, 118, 0.13, 21, "Near Colorless", 201, 1.27, 436, 0.66, 33, 
    "Spring", "January", 5, 14, 30   
],
2: [
    8.47, 125, 3.2, 0.13, 0.37, 0, 0, 0, 3.92, 146, 0.27, 8, "Near Colorless", 838, 0.24, 487, 0.03, 20, 
    "Stream", "August", 5, 0, 0  
]}




with gr.Blocks(theme=gr.themes.Default()) as demo:
    gr.Markdown("Water Quality Analysys System")
    with gr.Tab("Ручной ввод"):
        with gr.Accordion(label = "Химические показатели", open = False):
            with gr.Row():
                ph = gr.Slider(label="pH", minimum=0, maximum=14, step=0.1, value=7)
                
            with gr.Row():
                chloride = gr.Number(label="Chloride", minimum=0, maximum=1500, info="(mg/liter)")
                chlorine = gr.Number(label="Chlorine", minimum=0, maximum=20, info="(mg/liter)")
                copper = gr.Number(label="Copper", minimum=0, maximum=100, info=("μg/liter"))
                fluoride = gr.Number(label="Fluoride", minimum=0, maximum=20, info="(mg/liter)")
                iron = gr.Number(label="Iron", minimum=0, maximum=20, info="(mg/liter)")

            with gr.Row():
                lead = gr.Number(label="Lead", minimum=0, maximum=10, info="(μg/liter)")
                manganese = gr.Number(label="Manganese", minimum=0, maximum=30, info="(μg/liter)")
                nitrate = gr.Number(label="Nitrate", minimum=0, maximum=100, info="(mg/liter)")
                sulfate = gr.Number(label="Sulfate", minimum=0, maximum=1500, info="(μg/liter)")
                zinc = gr.Number(label="Zinc", minimum=0, maximum=30, info="(μg/liter)")

            

        with gr.Accordion(label = "Физические показатели", open = False):
            with gr.Row():
                water_temp = gr.Slider(label="Water Temperature", minimum=0, maximum=100, step=0.1, value=15, info=("(°C)"))
                color = gr.Dropdown(
                        label = "Color",
                        choices = [
                            "NA",
                            "Colorless",
                            "Faint Yellow",
                            "Light Yellow", 
                            "Near Colorless", 
                            "Yellow",
                        ],
                        value = "NA",
                        interactive=True,
                        allow_custom_value=False,
                )

            with gr.Row():
                conductivity = gr.Number(label="Conductivity", minimum=0, maximum=2500, info="(µS/cm)")                
                odor = gr.Number(label="Odor", minimum=0, maximum=5, info="(OU)")
                tds = gr.Number(label="Total Dissolved Solids", minimum=0, maximum=1500, info="(PPM)")
                turbidity = gr.Number(label="Turbidity", minimum=0, maximum=30, info="(NTU)")


                
        with gr.Accordion(label = "Показатели среды", open = False):
            
            with gr.Row():
                air_temp =gr.Slider(label="Air Temperature", minimum=-100, maximum=100, step=0.1, value=15, info=("(°C)"))
                source = gr.Dropdown(
                    label = "Source",
                    choices = [
                        "NA",
                        "Aquifer",
                        "Ground",
                        "Lake",
                        "Reservoir",
                        "River",
                        "Spring",
                        "Stream",
                        "Well"
                    ],
                    value = "NA",
                    interactive=True,
                    allow_custom_value=False,
                    )

            with gr.Row():
                month = gr.Dropdown(
                    label = "Month",
                    choices = list(months_days),
                    value = "NA",
                    interactive=True,
                    allow_custom_value=False,
                )
                
                day = gr.Dropdown(label = "Day", choices = list(range(1, months_days["NA"] + 1)),
                                  interactive=True,
                                      allow_custom_value=False,
                                      value = 1)
                def update_days(val):
                    day = gr.Dropdown(label = "Day", 
                                      choices = list(range(1, months_days[val] + 1)),
                                      interactive=True,
                                      allow_custom_value=False,
                                      value = 1
                                      )
                    return day

                month.input(update_days, month, day) 
                hour = gr.Dropdown(
                    label = "Hour",
                    choices = list(range(0, 24)),
                    value=0
                )
                minute = gr.Dropdown(
                    label = "Minute",
                    choices = list(range(0, 61)),
                    value=0
                )

        btn = gr.Button("Run")

        btn.click(fn=predict, inputs=[ph, iron, nitrate, chloride, lead, zinc, 
                                    turbidity, fluoride, copper, odor, sulfate, 
                                    conductivity, chlorine, manganese, tds, water_temp,
                                    color, air_temp, day, source, month, hour, minute], outputs=gr.HTML())
        
        example1=gr.Examples(label="Examples - safe water", inputs=[ph, chloride, chlorine, copper, fluoride, iron, lead, manganese, nitrate, sulfate,
                                      zinc, water_temp, color, conductivity, odor, tds, turbidity, air_temp, source,
                                        month, day, hour, minute],
                                 examples=[examples_good_dict[0], examples_good_dict[1], examples_good_dict[2]]       
                            )
        example2=gr.Examples(label="Examples - poor water", inputs=[ph, chloride, chlorine, copper, fluoride, iron, lead, manganese, nitrate, sulfate,
                                      zinc, water_temp, color, conductivity, odor, tds, turbidity, air_temp, source,
                                        month, day, hour, minute],
                                        examples=[examples_bad_dict[0], examples_bad_dict[1], examples_bad_dict[2]])


    
    with gr.Tab("Данные из датасета"):
        
        label_download = gr.Label(show_label=False, value="Click button below to download a template for your data")
        download_button = gr.DownloadButton(label = "Download template", value="C:/Users/etoth/Desktop/model/template.csv")

        label_upload = gr.Label(show_label=False, value="Click button below to upload your data")
        upload_button = gr.UploadButton(label = "Upload dataset", file_types=['.csv'])

        label_output = gr.Label(show_label=False, value="After you upload the file, a file with the results will appear in the area below")
        file_output = gr.File()

        upload_button.upload(predict_from_file, upload_button, file_output)


    with gr.Tab("Инструкция"):
        gr.HTML(label = "Инструкция", value = load_instructions())





demo.launch()




