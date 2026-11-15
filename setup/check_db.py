import os, psycopg

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    cur = conn.cursor()
    cur.execute("select extversion from pg_extension where extname='vector'")
    print("ok connected, pgvector", cur.fetchone()[0])

    cur.execute("select '[1,2,3]'::extensions.vector <=> '[1,2,4]'::extensions.vector")
    print("ok vector math works, distance =", cur.fetchone()[0])