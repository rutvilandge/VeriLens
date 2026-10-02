import fs from "node:fs";
import os from "node:os";
import path from "node:path";

export const uploadRoot = process.env.VERCEL === "1"
  ? path.join(os.tmpdir(), "verilens-uploads")
  : path.resolve(process.cwd(), "uploads");
export const imageUploadDirectory = path.join(uploadRoot, "images");

export function ensureImageUploadDirectory() {
  fs.mkdirSync(imageUploadDirectory, { recursive: true });
}

export function resolveStoredUpload(fileUrl: string) {
  if (!fileUrl.startsWith("/uploads/")) return null;
  const target = path.resolve(uploadRoot, fileUrl.slice("/uploads/".length));
  if (!target.startsWith(`${uploadRoot}${path.sep}`)) return null;
  return target;
}

export function imagePublicUrl(filename: string) {
  return `/uploads/images/${path.basename(filename)}`;
}

export function hasValidImageSignature(filePath: string, mimeType: string) {
  const header = Buffer.alloc(12);
  const fd = fs.openSync(filePath, "r");
  try { fs.readSync(fd, header, 0, header.length, 0); }
  finally { fs.closeSync(fd); }
  if (mimeType === "image/jpeg") return header[0] === 0xff && header[1] === 0xd8 && header[2] === 0xff;
  if (mimeType === "image/png") return header.subarray(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]));
  if (mimeType === "image/webp") return header.toString("ascii", 0, 4) === "RIFF" && header.toString("ascii", 8, 12) === "WEBP";
  return false;
}
