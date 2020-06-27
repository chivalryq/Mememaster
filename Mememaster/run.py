from .mememaster import app

if __name__=="__main__":
    print(app.url_map)
    app.run(debug = True,port=5123)
