# Currently not working properly due to harsh refactoring !

## To-be-fixed after my graduation

# VoidWave (Gaming Platform) 

This project was created for the Process Management Database course at the Faculty of Mechanical Engineering Brno University of Technology (FME BUT). This course is part of the winterr semester for 3rd-year students in the Applied Computer Science and Control program. 

## Overview
The goal of this project was to create a web application centered around a self-designed relational database. VoidWave serves as a platform for gaming community, team formation, event participation, and social mechanics like send friend request that simulate real-world interactions found on major community platforms like Discord.

To mimic a living ecosystem, the system uses a custom command "simulation". This command deletes data and adds new to database with authentic, time-accurate events that strictly adhere to the program's constraints. The overall aesthetic is inspired by the Vaporwave.

## Toolbox
**Backend:** Python, Django
**Frontend:** HTML, CSS
**Database:** SQLite

## Contents
`core`– contains the Django logic, models (Tim, Rebricek, Umiestnenie), and the ranking engine
`platform_config `– configurations for the Django environment
`static`– visual assets and stylesheets that create VoidWave aesthetic
`database_design.pdf`– scheme of the relational database 
`manage.py`– entry point for admin tasks and server execution

## Run project

1. Initialize your data store and apply the relational migrations
````bash
python manage.py makemirations
python manage.py migrate
````
2. Create your superuser account.
````bash
python manage.py createsuperuser
````
3. Start the server and manage the process via the Django Admin Interface.
````bash
python manage.py runserver
````
3. Navigate to http://127.0.0.1:8000/ printed in terminal.

---

**Name:** Val (calex404)
**Date:** December 2025
