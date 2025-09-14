from website import create_app

app = create_app()

def pluralize_filter(number, singular, plural=None):
    if number == 1:
        return singular
    else:
        return plural if plural is not None else singular + 's'

app.jinja_env.filters['pluralize'] = pluralize_filter

if __name__ == '__main__':
    app.run(debug=True)