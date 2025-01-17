# Use the official Node.js image for React development
FROM node:22.12.0-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to the container
COPY package*.json .

# Install dependencies
RUN npm install

# Copy the rest of the application files to the container
COPY . ./

# Expose the development server port
EXPOSE 3000

# Start the React development server
CMD ["npm", "start"]
