from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

try:
    conn = psycopg2.connect(
        host="localhost",
        database="fastapi",
        user="postgres",
        password="sN&071158",
        cursor_factory=RealDictCursor
    )

    cursor = conn.cursor()
    print("Database connection successful!")

except Exception as error:
    print("Database connection failed")
    print(error)

@app.get("/posts")
def get_posts():
    cursor.execute(""" SELECT * FROM POSTS """)
    posts = cursor.fetchall()
    print(posts)
    return {"data":posts}

@app.post("/posts")
def create_post(post: Post):
   cursor.execute(""" INSERT INTO POSTS (title, content, published) VALUES (%s, %s, %s) RETURNING * """, 
                  (post.title, post.content,post.published))
   new_post = cursor.fetchone()
   conn.commit()

   return {"data":new_post}

@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute(""" SELECT * FROM POSTS WHERE ID = %s """, (id,))
    post = cursor.fetchone()
    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="post not found")
    return {"post_detail":post}

@app.delete("/posts{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute(""" DELETE FROM POSTS WHERE ID = %s  RETURNING * """, (id,))
    delete_post = cursor.fetchone()
    conn.commit()

    if delete_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")   
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """,(post.title, post.content, post.published, id))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found")

    return {"updated_post": updated_post}

@app.get("/")
def root():
    return {"message": "API is running"}