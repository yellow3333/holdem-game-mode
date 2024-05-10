# single player v.s multi_ai players
------------------------------------------------
NOTE: BACKUP BEFORE CHANGING THE CODE
# Files / directoies

## backup model:
此資料夾僅用於檔案備份非正確路徑，請在其他資料夾執行程式碼

## officialAI:
運行的code
### ai_model.py
傳資料到AI
### old_cnn.py
對資料轉成old cnn的格式
個別處理ALLIN跟FOLD
### old_rf.py
對資料轉成old rf的格式
個別處理ALLIN跟FOLD
### new_cnn.py
對資料轉成new cnn的格式
個別處理ALLIN

## documents:
資料文件

## domain:
遊戲物件

## static:
poker js css image

## templates:
html

## NCmodel:
112屆訓練好的CNN model
3 players: model3
4 players: model4
3+4 players: anothor model can be used for both 3 and 4 players 

## OCmodel:
111屆訓練好的CNN model

## RFmodel:
110屆訓練好的CNN model
----------------------------------------------------------
# How to run it?
1.pip install the required packages in the requirement.txt

2.Change the model path if the file is not installed in E:\\ 

## Change paths in the following python files
# (use ctrl+f to find #path)

### old_cnn.py 
```python 

    def predict(self):
        with open('E:\\TexasPoker\\OCmodel\\model.config', 'r') as text_file: #path
            json_string = text_file.read()
        model = Sequential()
        model = model_from_json(json_string)
        model.load_weights("E:\\TexasPoker\\OCmodel\\model.weight", by_name=False) #path
    
```
### old_rf.py 
```python
    def predict(self):
        model = joblib.load(r"E:\TexasPoker\RFmodel\my_random_forest.joblib")  #path 
		#change to your file path
        action = int(float(model.predict(np.array(self.game_data).reshape(1, -1))))
        self.print_game_data()
        print("RF predict number:",action)
        predict_action=self.get_predict_action(action)
        print("RF predict action: ",predict_action)
        return predict_action 
```

### new_cnn.py 
```python
    def predict(self):
        
        if self.get_players()==3:
            with open("E:\\TexasPoker\\NCmodel\\model-3p\\model3.config", "r") as json_file:#path
                json_string = json_file.read()
            model = Sequential()
            model = model_from_json(json_string)
            model.load_weights("E:\\TexasPoker\\NCmodel\\model-3p\\model3.weight", by_name=False) #path
        elif self.get_players()==4:
            with open("E:\\TexasPoker\\NCmodel\\model-4p\\model4.config", "r") as json_file:#path
                json_string = json_file.read()
            model = Sequential()
            model = model_from_json(json_string)
            model.load_weights("E:\\TexasPoker\\NCmodel\\model-4p\\model4.weight", by_name=False) #path
```

3.compile and run app.py, press ctrl and click the url

-------------------------------------------------------------------------------------------
# Running Texas Poker
1. Press New Table for choosing the player numbers and initialize all players' chips amount
2. Press New game for another round 
3. Press Rules for instructions
--------------------------------------------------------------------------------------------
# Bug fixed
Most bug can be fixed by pressing New table or restarting the app.py 


