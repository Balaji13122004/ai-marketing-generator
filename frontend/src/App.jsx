import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import GenerationPanel from './components/GenerationPanel';
import RefinementPanel from './components/RefinementPanel';
import ImageLibrary from './components/ImageLibrary';
import ImagePreviewModal from './components/ImagePreviewModal';
import { apiService } from './services/api';

export default function App() {
  const [brands, setBrands] = useState([]);
  const [threadData, setThreadData] = useState(null);
  const [libraryImages, setLibraryImages] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [generateError, setGenerateError] = useState(null);
  const [refineError, setRefineError] = useState(null);
  const [previewImage, setPreviewImage] = useState(null);

  // Library filters
  const [libAppFilter, setLibAppFilter] = useState('All');
  const [libTypeFilter, setLibTypeFilter] = useState('All');

  // Load brands on mount
  useEffect(() => {
    async function loadBrands() {
      try {
        const data = await apiService.getBrandProfiles();
        setBrands(data);
      } catch (err) {
        console.error('Failed to load brand profiles:', err);
      }
    }
    loadBrands();
  }, []);

  // Load library images
  const loadLibrary = useCallback(async () => {
    try {
      const data = await apiService.getImageLibrary({
        app_name: libAppFilter,
        image_type: libTypeFilter,
      });
      setLibraryImages(data);
    } catch (err) {
      console.error('Failed to load library images:', err);
    }
  }, [libAppFilter, libTypeFilter]);

  useEffect(() => {
    loadLibrary();
  }, [loadLibrary]);

  // Handle new thread generation
  const handleGenerate = async (params) => {
    setIsGenerating(true);
    setGenerateError(null);
    try {
      const response = await apiService.createThread(params);
      const threadId = response.thread_id;
      
      // Load complete thread details
      const fullThread = await apiService.getThreadDetail(threadId);
      setThreadData(fullThread);

      // Refresh library
      loadLibrary();

      // Smooth scroll to refinement panel
      setTimeout(() => {
        const el = document.getElementById('refinement-panel');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 300);
    } catch (err) {
      console.error('Generation error:', err);
      const errorMsg =
        err.response?.data?.error ||
        err.message ||
        'Failed to generate images. Check API credentials or network connection.';
      setGenerateError(errorMsg);
    } finally {
      setIsGenerating(false);
    }
  };

  // Handle refinement loop
  const handleRefine = async ({ selected_image_id, refinement_instruction }) => {
    if (!threadData) return;
    setIsRefining(true);
    setRefineError(null);
    try {
      await apiService.refineThread(threadData.thread_id, {
        selected_image_id,
        refinement_instruction,
      });

      // Reload full thread detail to get accumulated round trail
      const updated = await apiService.getThreadDetail(threadData.thread_id);
      setThreadData(updated);

      // Refresh library
      loadLibrary();
    } catch (err) {
      console.error('Refinement error:', err);
      const errorMsg =
        err.response?.data?.error ||
        err.message ||
        'Refinement request failed.';
      setRefineError(errorMsg);
    } finally {
      setIsRefining(false);
    }
  };

  // Handle mark image as chosen/finalized
  const handleSelectImage = async (imageId) => {
    try {
      await apiService.selectImage(imageId);
      // Refresh current thread and library
      if (threadData) {
        const updated = await apiService.getThreadDetail(threadData.thread_id);
        setThreadData(updated);
      }
      loadLibrary();
    } catch (err) {
      console.error('Select image error:', err);
    }
  };

  return (
    <div className="min-vh-100 d-flex flex-column pb-5">
      <Navbar brandCount={brands.length} libraryCount={libraryImages.length} />

      <main className="container flex-grow-1">
        {/* Section 1: Generation Panel */}
        <GenerationPanel
          brands={brands}
          onGenerate={handleGenerate}
          isGenerating={isGenerating}
          error={generateError}
          onDismissError={() => setGenerateError(null)}
        />

        {/* Section 2: Refinement Chat Panel */}
        <RefinementPanel
          threadData={threadData}
          onRefine={handleRefine}
          isRefining={isRefining}
          onSelectImage={handleSelectImage}
          onPreviewImage={(img) => setPreviewImage(img)}
          refineError={refineError}
        />

        {/* Section 3: Image Library */}
        <ImageLibrary
          images={libraryImages}
          brands={brands}
          selectedApp={libAppFilter}
          onAppFilterChange={setLibAppFilter}
          selectedType={libTypeFilter}
          onTypeFilterChange={setLibTypeFilter}
          onPreviewImage={(img) => setPreviewImage(img)}
          onRefresh={loadLibrary}
        />
      </main>

      {/* Image Preview Modal */}
      {previewImage && (
        <ImagePreviewModal
          image={previewImage}
          onClose={() => setPreviewImage(null)}
        />
      )}

      <footer className="container text-center py-4 border-top mt-5 text-muted small">
        FS-7 AI-Powered Image Generation Platform • Django REST Framework & React • Parametric Pillow Engine
      </footer>
    </div>
  );
}
