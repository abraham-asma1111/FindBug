'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import { X, Download, ZoomIn, ZoomOut, RotateCw, Play, Pause, Volume2, VolumeX, Maximize } from 'lucide-react';

interface Attachment {
  id: string;
  filename: string;
  original_filename?: string;
  file_type: string;
  file_size: number;
  storage_path: string;
  uploaded_at?: string;
}

interface MediaViewerProps {
  attachments: Attachment[];
  initialIndex?: number;
  isOpen: boolean;
  onClose: () => void;
}

export default function MediaViewer({ attachments, initialIndex = 0, isOpen, onClose }: MediaViewerProps) {
  const [currentIndex, setCurrentIndex] = useState(initialIndex);
  const [zoom, setZoom] = useState(100);
  const [rotation, setRotation] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [videoElement, setVideoElement] = useState<HTMLVideoElement | null>(null);

  const currentAttachment = attachments[currentIndex];
  const fileUrl = `/api/v1/files/serve/${currentAttachment?.storage_path}`;

  const isImage = currentAttachment?.file_type?.startsWith('image/');
  const isVideo = currentAttachment?.file_type?.startsWith('video/');
  const isPDF = currentAttachment?.file_type === 'application/pdf';

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      resetControls();
    }
  };

  const handleNext = () => {
    if (currentIndex < attachments.length - 1) {
      setCurrentIndex(currentIndex + 1);
      resetControls();
    }
  };

  const resetControls = () => {
    setZoom(100);
    setRotation(0);
    setIsPlaying(false);
  };

  const handleZoomIn = () => {
    setZoom(Math.min(zoom + 25, 200));
  };

  const handleZoomOut = () => {
    setZoom(Math.max(zoom - 25, 50));
  };

  const handleRotate = () => {
    setRotation((rotation + 90) % 360);
  };

  const handlePlayPause = () => {
    if (videoElement) {
      if (isPlaying) {
        videoElement.pause();
      } else {
        videoElement.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleMuteToggle = () => {
    if (videoElement) {
      videoElement.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = fileUrl;
    link.download = currentAttachment.original_filename || currentAttachment.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  if (!currentAttachment) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="full">
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#e6ddd4] dark:border-gray-800">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-[#2d2a26] dark:text-white">
              {currentAttachment.original_filename || currentAttachment.filename}
            </h3>
            <p className="text-sm text-[#6d6760] dark:text-gray-400">
              {currentAttachment.file_type} • {formatFileSize(currentAttachment.file_size)}
              {attachments.length > 1 && ` • ${currentIndex + 1} of ${attachments.length}`}
            </p>
          </div>
          
          {/* Controls */}
          <div className="flex items-center gap-2">
            {isImage && (
              <>
                <button
                  onClick={handleZoomOut}
                  className="p-2 rounded-lg hover:bg-[#faf6f1] dark:hover:bg-neutral-800 transition"
                  title="Zoom Out"
                >
                  <ZoomOut className="h-5 w-5 text-[#2d2a26] dark:text-white" />
                </button>
                <span className="text-sm text-[#6d6760] dark:text-gray-400 min-w-[60px] text-center">
                  {zoom}%
                </span>
                <button
                  onClick={handleZoomIn}
                  className="p-2 rounded-lg hover:bg-[#faf6f1] dark:hover:bg-neutral-800 transition"
                  title="Zoom In"
                >
                  <ZoomIn className="h-5 w-5 text-[#2d2a26] dark:text-white" />
                </button>
                <button
                  onClick={handleRotate}
                  className="p-2 rounded-lg hover:bg-[#faf6f1] dark:hover:bg-neutral-800 transition"
                  title="Rotate"
                >
                  <RotateCw className="h-5 w-5 text-[#2d2a26] dark:text-white" />
                </button>
              </>
            )}
            
            <button
              onClick={handleDownload}
              className="p-2 rounded-lg hover:bg-[#faf6f1] dark:hover:bg-neutral-800 transition"
              title="Download"
            >
              <Download className="h-5 w-5 text-[#2d2a26] dark:text-white" />
            </button>
            
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-[#faf6f1] dark:hover:bg-neutral-800 transition"
              title="Close"
            >
              <X className="h-5 w-5 text-[#2d2a26] dark:text-white" />
            </button>
          </div>
        </div>

        {/* Media Content */}
        <div className="flex-1 flex items-center justify-center bg-[#faf6f1] dark:bg-black p-8 overflow-hidden">
          {isImage && (
            <img
              src={fileUrl}
              alt={currentAttachment.filename}
              className="max-w-full max-h-full object-contain transition-transform duration-200"
              style={{
                transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
              }}
            />
          )}

          {isVideo && (
            <div className="relative max-w-full max-h-full">
              <video
                ref={setVideoElement}
                src={fileUrl}
                className="max-w-full max-h-full"
                controls
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
              >
                Your browser does not support the video tag.
              </video>
            </div>
          )}

          {isPDF && (
            <iframe
              src={fileUrl}
              className="w-full h-full border-0"
              title={currentAttachment.filename}
            />
          )}

          {!isImage && !isVideo && !isPDF && (
            <div className="text-center">
              <div className="mb-4">
                <svg
                  className="h-16 w-16 mx-auto text-[#8b8177] dark:text-gray-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <p className="text-[#6d6760] dark:text-gray-400 mb-4">
                Preview not available for this file type
              </p>
              <button
                onClick={handleDownload}
                className="inline-flex items-center gap-2 rounded-full bg-[#ef2330] px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-[#d41f2c]"
              >
                <Download className="h-4 w-4" />
                Download File
              </button>
            </div>
          )}
        </div>

        {/* Navigation Footer */}
        {attachments.length > 1 && (
          <div className="flex items-center justify-between p-4 border-t border-[#e6ddd4] dark:border-gray-800">
            <button
              onClick={handlePrevious}
              disabled={currentIndex === 0}
              className="inline-flex items-center gap-2 rounded-full border border-[#d8d0c8] dark:border-gray-700 px-4 py-2 text-sm font-semibold text-[#2d2a26] dark:text-white transition hover:bg-[#faf6f1] dark:hover:bg-neutral-800 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Previous
            </button>

            <div className="flex gap-2">
              {attachments.map((_, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setCurrentIndex(index);
                    resetControls();
                  }}
                  className={`h-2 w-2 rounded-full transition ${
                    index === currentIndex
                      ? 'bg-[#ef2330] w-6'
                      : 'bg-[#d8d0c8] dark:bg-gray-700 hover:bg-[#c8bfb6] dark:hover:bg-gray-600'
                  }`}
                  title={`View ${attachments[index].filename}`}
                />
              ))}
            </div>

            <button
              onClick={handleNext}
              disabled={currentIndex === attachments.length - 1}
              className="inline-flex items-center gap-2 rounded-full border border-[#d8d0c8] dark:border-gray-700 px-4 py-2 text-sm font-semibold text-[#2d2a26] dark:text-white transition hover:bg-[#faf6f1] dark:hover:bg-neutral-800 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        )}
      </div>
    </Modal>
  );
}
