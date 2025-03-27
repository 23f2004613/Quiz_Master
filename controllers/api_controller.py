from flask_restful import Api,Resource
from flask import request
from models.models import *


api= Api()


class ChapterApi(Resource):

    def get(self):  #reading the data
        chapters = Chapter.query.all()
        chap_json=[]
        for chap in chapters:
            chap_json.append({'id':chap.id,'name':chap.name,'description':chap.description,'Subject_id':chap.Subject_id,})
        return chap_json,200



    def post(self): #creating the data
        name = request.json.get("name")
        description = request.json.get("description") 
        subject_id = request.json.get("Subject_id")
        new_chapter = Chapter(name=name,description=description,Subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        return {"messege":"New chapter added!"},201


    def put(self,id):  # updating the data
        chapter = Chapter.query.filter_by(id=id).first()
        if chapter:
            chapter.name = request.json.get("name")
            chapter.description = request.json.get("description") 
            chapter.Subject_id = request.json.get("Subject_id")
            db.session.commit()
            return {"messege":"chapter updated!"},200
        return {"messege": "chapter not found"},404


    def delete(self,id):  #deleting the data
        chapter = Chapter.query.filter_by(id=id).first()
        if chapter:
            db.session.delete(chapter)
            db.session.commit()
            return {"messege":"chapter deleted!"},200
        return {"messege": "chapter not found"},404


api.add_resource(ChapterApi,"/api/get_chapters","/api/add_chapters","/api/edit_chapters/<id>","/api/delete_chapters/<id>")