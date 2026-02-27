FROM node:20-alpine

WORKDIR /app

# Копируем package.json и устанавливаем зависимости
COPY package.json package-lock.json ./
RUN npm install

# Копируем весь код
COPY . .

# Vite по умолчанию использует порт 5173
EXPOSE 5173

# Запуск в режиме разработки с хостом 0.0.0.0 (важно для Docker!)
CMD ["npm", "run", "dev", "--", "--host"]