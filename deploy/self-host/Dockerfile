# One instance, one database, one person. The database lives on a volume at
# /data so a new container does not lose it.
FROM node:22-bookworm-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends openssl ca-certificates \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /repo
COPY . .
RUN npm --prefix app ci
RUN cd app && npx prisma generate
RUN npm --prefix app run build
ENV NODE_ENV=production \
    DATABASE_URL=file:/data/dev.db \
    HOST=0.0.0.0 \
    PORT=4321
VOLUME ["/data"]
EXPOSE 4321
CMD ["sh", "-c", "cd app && npx prisma db push --skip-generate && node scripts/migrate.mjs && node dist/server/entry.mjs"]
