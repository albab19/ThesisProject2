FROM node



# COPY package*.json .
COPY . .

WORKDIR /.
RUN npm install &&  npm rebuild sqlite3 && npm install redis
EXPOSE 3000

CMD ["node", "app.js"] 
