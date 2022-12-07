from flask import Flask

app=Flask(_name_)
@app.route('/')
    def index():
        return "hello world";