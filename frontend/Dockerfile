# Image épinglée (pas :latest) pour éviter les dérives silencieuses
FROM node:22.17.1-alpine3.22

WORKDIR /app

RUN addgroup -S app && adduser -S app -G app

COPY package.json ./
RUN npm install \
    && chown -R app:app /app

COPY --chown=app:app . .

USER app

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
