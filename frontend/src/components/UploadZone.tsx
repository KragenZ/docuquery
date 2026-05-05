"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, File, CheckCircle, Loader2 } from "lucide-react";
import { uploadDocument } from "@/lib/api";
import { cn } from "@/lib/utils";

interface Props {
  onUploadSuccess: () => void;
}

export default function UploadZone({ onUploadSuccess }: Props) {
  const [isUploading, setIsUploading] = useState(false);
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    try {
      setIsUploading(true);
      setStatus("uploading");
      await uploadDocument(file);
      setStatus("success");
      onUploadSuccess();
      
      // reset after a bit
      setTimeout(() => setStatus("idle"), 3000);
    } catch (err) {
      console.error(err);
      setStatus("error");
    } finally {
      setIsUploading(false);
    }
  }, [onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        "border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors",
        isDragActive ? "border-primary bg-primary/10" : "border-border hover:border-primary/50 glass",
        isUploading && "opacity-50 cursor-not-allowed"
      )}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center justify-center gap-4">
        {status === "uploading" ? (
          <Loader2 className="w-10 h-10 text-primary animate-spin" />
        ) : status === "success" ? (
          <CheckCircle className="w-10 h-10 text-green-500" />
        ) : (
          <UploadCloud className={cn("w-10 h-10 text-text-muted", isDragActive && "text-primary")} />
        )}
        
        <div>
          <p className="font-medium text-text">
            {isDragActive ? "Drop PDF here" : "Click or drag a PDF to upload"}
          </p>
          <p className="text-sm text-text-muted mt-1">
            Max file size: 10MB
          </p>
        </div>
      </div>
    </div>
  );
}
