# sinpp - Schedule-i-nator++
A tool for scheduling volunteers during speedrunning events made using Django and TypeScript. You can follow the project's development on my dedicated [Vikunja list](https://vikunja.pokerfacowaty.com/share/VKLuDzhaPqYzarGOgCXlEijbvELSJdyojzvRpcik/auth).

## Installation

### With Docker:
This option requires you to have [Docker](https://docs.docker.com/engine/install/) installed.
1. Download the newest release or (if there's no release available yet) clone the repository with `git clone https://github.com/PokerFacowaty/sinpp` and enter its directory.
2. Edit `docker-compose.yml`, set up environment variables, don't forget to add a volume if you need one for static files.
    - Don't forget you need a server such as Nginx or Apache to serve static files in a Django production environment `(as in, when DEBUG is set to False)`. More info on doing that can be found [here](https://docs.djangoproject.com/en/4.2/howto/static-files/). My personal recommendation would be to use the [Nginx Proxy Manager](https://nginxproxymanager.com/) and add a location for static files for the proxy in the Advanced tab, e.x.
        ```
        location /static {
        autoindex on;
        alias /data/www/static/;
        }
        ```
3. Run `docker compose up -d` to build and start a container from the `docker-compose.yml` file in detached mode or omit the `-d` option to attach to it once it's running. More on docker compose can be found [here](https://docs.docker.com/compose/compose-file/build/).

### With poetry:
This option requires you to have a [PostgreSQL](https://www.postgresql.org/download/) server set up, as well as [poetry](https://python-poetry.org/docs/) and [TypeScript](https://www.typescriptlang.org/id/download) installed. This is not the recommended way, use it only if you really want to run sinpp on bare metal.
1. Download the newest release or (if there's no release available yet) clone the repository with `git clone https://github.com/PokerFacowaty/sinpp` and enter its directory.
2. Install all dependencies with `poetry install --no-root`
3. Transpile all TypeScript files into JavaScript with `tsc`.
4. Set up environment variables listed in the `docker-compose.yml` file either inside in the poetry's virtual environment or in a `.env` file in the repository's root directory.
    - Don't forget you need a server such as Nginx or Apache to serve static files in a Django production environment `(as in, when DEBUG is set to False)`. More info on doing that can be found [here](https://docs.djangoproject.com/en/4.2/howto/static-files/). My personal recommendation would be to use the [Nginx Proxy Manager](https://nginxproxymanager.com/) and add a location for static files for the proxy in the Advanced tab, e.x.
        ```
        location /static {
        autoindex on;
        alias /data/www/static/;
        }
        ```
5. Migrate all the models into the database by running `poetry run python3 manage.py makemigrations` and `poetry run python3 manage.py migrate`.
    - Keepn in mind `python3` might be named differently on your system.
6. Move all the static files to STATIC_ROOT with `poetry run python3 manage.py collectstatic --no-input --clear`.
7. Start the server by running `poetry run python3 manage.py runserver 0.0.0.0:8000` replacing `8000` with the port you want to run the server on.

## Development
The recommended way for development is to use Docker with the `docker-compose-dev.yml` (which also uses the Dockerimage-dev file) to build and start the containers and attach to the container should you need to transpile TypeScript. The source code is then attached as a volume, so you can see the changes live.

Currently all tests available in the `schedule` module are outdated, since they rely on old models schema from before I made any views or front end. Getting proper tests in place is one of my current priorities for the project.

## FAQ
- Can I use a different database other than PostgreSQL?
- [This](https://docs.djangoproject.com/en/4.2/ref/models/fields/#durationfield) is the reason sinpp uses PostgreSQL. You can use any other database, but you'll do so at your own risk of one of the most crucial functionalities of a scheduling app not working as expected. You have been warned ;)

- Where does the name come from?
- Back when I couldn't program yet but also couldn't stand scheduling Fundraising volunteers for ESA manually, I made a Google Spreadsheet called "Volunteer Schedule-i-nator". It took me 2 weekends of almost non-stop work and research, took a solid 15 - 20 minutes to process the games' schedule every time and was very ambitious with its supposed capabilities - handling 5 teams of volunteers, up to 50 volunteers total, optional singup system through Google Forms (though I completely forgot about adding accepting and rejecting volunteers). Despite its obvious flaws, if used carefully and with capable spreadsheets hackers within reach for emergencies (shoutouts to [@Zet](https://www.twitch.tv/zet237)), it actually was quite a bit faster than manual scheduling. This is the extended version of the original idea, hence the "++".