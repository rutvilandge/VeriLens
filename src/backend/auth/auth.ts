import "dotenv/config";
import { ExpressAuth } from "@auth/express";
import Credentials from "@auth/express/providers/credentials";
import bcrypt from "bcrypt";

import { prisma } from "../lib/prisma.js";

const frontendUrl = (process.env.FRONTEND_URL || (process.env.NODE_ENV === "production" ? "" : "http://localhost:3000")).split(",").map((value) => value.trim()).filter(Boolean)[0] || "";
if (process.env.NODE_ENV === "production" && !process.env.AUTH_SECRET) throw new Error("AUTH_SECRET is required in production.");
if (process.env.NODE_ENV === "production" && !process.env.AUTH_URL) throw new Error("AUTH_URL is required in production.");
if (process.env.NODE_ENV === "production" && !frontendUrl) throw new Error("FRONTEND_URL is required in production.");

export const authConfig = {
  secret: process.env.AUTH_SECRET,

  trustHost: process.env.AUTH_TRUST_HOST !== "false",

  session: {
    strategy: "jwt" as const,
  },

  callbacks: {
    async redirect({
      url,
      baseUrl,
    }: {
      url: string;
      baseUrl: string;
    }) {
      if (url.startsWith("/")) {
        return `${frontendUrl}${url}`;
      }

      try {
        const requestedUrl = new URL(url);

        if (requestedUrl.origin === frontendUrl) {
          return url;
        }
      } catch {
        // Fall back to the frontend URL below.
      }

      return frontendUrl || baseUrl;
    },
  },

  providers: [
    Credentials({
      name: "Credentials",

      credentials: {
        email: {
          label: "Email",
          type: "email",
        },

        password: {
          label: "Password",
          type: "password",
        },
      },

      async authorize(credentials) {
        const email = String(credentials?.email ?? "")
          .trim()
          .toLowerCase();

        const password = String(credentials?.password ?? "");

        if (!email || !password) {
          return null;
        }

        const user = await prisma.user.findUnique({
          where: {
            email,
          },
        });

        if (!user) {
          return null;
        }

        const passwordValid = await bcrypt.compare(
          password,
          user.passwordHash,
        );

        if (!passwordValid) {
          return null;
        }

        return {
          id: user.id,
          name: user.name,
          email: user.email,
        };
      },
    }),
  ],
};

export const authHandler = ExpressAuth(authConfig);

