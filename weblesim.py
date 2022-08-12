from website import create_app

appli = create_app()

if __name__ == '__main__':
    appli.run(debug=True)
