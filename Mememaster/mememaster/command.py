from ..mememaster import db, app
import click


@app.cli.command()
@click.option('--drop', is_flag=True, help='create after drop')
def initdb(drop):
    if(drop):
        click.confirm(
            'delete the databse???do not use this in production!', abort=True)
        db.drop_all()
        click.echo('drop tables')
    db.create_all()
    click.echo('create database')
