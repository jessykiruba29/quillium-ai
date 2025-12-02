'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

import { Hero } from './components/sections/Hero'
import { FileUploadZone } from './components/sections/FileUpload'
import { QuizInterface } from './components/sections/Quiz'
import { FlashcardHolo } from './components/sections/Flashcards'
import { ProgressDashboard } from './components/sections/Progress'
import { LanguageSelector } from './components/sections/Language'
import { Navigation } from './components/layout/Navigation'
import { LoadingOrb } from './components/ui/LoadingOrb'
import { StarField } from './components/effects/StarField'
import { uploadPDF } from '@/lib/api/client'
import { MCQ, Flashcard, ProgressData } from '@/types'

type View = 'hero' | 'upload' | 'quiz' | 'flashcards' | 'progress'

export default function Home() {
  const [currentView, setCurrentView] = useState<View>('hero')
  const [selectedLanguage, setSelectedLanguage] = useState('English')
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [processedData, setProcessedData] = useState<{
    text: string
    mcqs: MCQ[]
    flashcards: Flashcard[]
    pageCount: number
    language: string
  } | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState<ProgressData>({
    totalQuestions: 0,
    correctAnswers: 0,
    incorrectAnswers: 0,
    quizzesTaken: 0,
    flashcardsStudied: 0,
  })

  useEffect(() => {
    // Check if we have data in localStorage
    try {
      const savedData = localStorage.getItem('quillium_data')
      const savedProgress = localStorage.getItem('quillium_progress')
      const savedLanguage = localStorage.getItem('quillium_language')
      
      if (savedData) {
        const parsedData = JSON.parse(savedData)
        if (parsedData && typeof parsedData === 'object' && 'mcqs' in parsedData) {
          setProcessedData(parsedData)
        }
      }
      
      if (savedProgress) {
        const parsedProgress = JSON.parse(savedProgress)
        if (parsedProgress && typeof parsedProgress === 'object') {
          setProgress(parsedProgress)
        }
      }
      
      if (savedLanguage) {
        setSelectedLanguage(savedLanguage)
      }
    } catch (error) {
      console.error('Error loading from localStorage:', error)
    }
  }, [])

  const handleFileUpload = async (file: File) => {
    setIsProcessing(true)
    setUploadedFile(file)
    
    try {
      // Pass selected language to API
      const response = await uploadPDF(file, selectedLanguage, 20)
      
      // Handle API response
      const apiData = response.data || response
      
      const formattedData = {
        text: apiData.text || "Text extracted from PDF",
        mcqs: apiData.mcqs || [],
        flashcards: apiData.flashcards || [],
        pageCount: apiData.page_count || 1,
        language: selectedLanguage
      }
      
      setProcessedData(formattedData)
      
      // Save to localStorage
      try {
        localStorage.setItem('quillium_data', JSON.stringify(formattedData))
        localStorage.setItem('quillium_language', selectedLanguage)
      } catch (error) {
        console.error('Failed to save to localStorage:', error)
      }
      
      setCurrentView('quiz')
    } catch (error) {
      console.error('Upload failed:', error)
      alert('Failed to process PDF. Please try again.')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleLanguageChange = (language: string) => {
    setSelectedLanguage(language)
    localStorage.setItem('quillium_language', language)
    
    // If we have processed data, we should reprocess with new language
    if (processedData && uploadedFile) {
      alert(`Language changed to ${language}. Re-upload the file to translate content.`)
    }
  }

  const handleQuizAnswer = (isCorrect: boolean) => {
    setProgress(prev => {
      const newProgress = {
        ...prev,
        totalQuestions: prev.totalQuestions + 1,
        correctAnswers: prev.correctAnswers + (isCorrect ? 1 : 0),
        incorrectAnswers: prev.incorrectAnswers + (isCorrect ? 0 : 1),
        quizzesTaken: prev.quizzesTaken + 1,
      }
      
      try {
        localStorage.setItem('quillium_progress', JSON.stringify(newProgress))
      } catch (error) {
        console.error('Failed to save progress:', error)
      }
      
      return newProgress
    })
  }

  const handleFlashcardStudy = () => {
    setProgress(prev => {
      const newProgress = {
        ...prev,
        flashcardsStudied: prev.flashcardsStudied + 1
      }
      
      try {
        localStorage.setItem('quillium_progress', JSON.stringify(newProgress))
      } catch (error) {
        console.error('Failed to save progress:', error)
      }
      
      return newProgress
    })
  }

  const navigateTo = (view: View) => {
    setCurrentView(view)
  }

  const clearLocalStorage = () => {
    localStorage.removeItem('quillium_data')
    localStorage.removeItem('quillium_progress')
    localStorage.removeItem('quillium_language')
    setProcessedData(null)
    setProgress({
      totalQuestions: 0,
      correctAnswers: 0,
      incorrectAnswers: 0,
      quizzesTaken: 0,
      flashcardsStudied: 0,
    })
    setCurrentView('upload')
  }

  const pageVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { 
      opacity: 1, 
      y: 0,
      transition: { 
        type: "spring",
        stiffness: 100,
        damping: 20,
        staggerChildren: 0.1
      }
    },
    exit: { 
      opacity: 0, 
      y: -20,
      transition: { duration: 0.3 }
    }
  }

  return (
    <div className="relative min-h-screen">
      <StarField />
      
      <AnimatePresence mode="wait">
        {currentView === 'hero' && (
         
            <Hero onGetStarted={() => navigateTo('upload')} />
        )}

        {currentView === 'upload' && (
         
            <div className="max-w-6xl mx-auto">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2">
                  <FileUploadZone 
                    onFileUpload={handleFileUpload}
                    isProcessing={isProcessing}
                  />
                </div>
                <div className="lg:col-span-1 space-y-6">
                  {/* Language Selector */}
                  <LanguageSelector 
                    selectedLanguage={selectedLanguage}
                    onLanguageChange={handleLanguageChange}
                  />
                  
                  {/* Processing Indicator */}
                  {isProcessing && (
                    <div className="holographic-card p-6 rounded-2xl">
                      <LoadingOrb />
                      <h3 className="text-xl font-bold text-white mb-2 mt-4">
                        Processing in {selectedLanguage}
                      </h3>
                      <p className="text-cyan-400/70">Translating content...</p>
                    </div>
                  )}
                  
                  {/* Clear Data Button */}
                  {processedData && (
                    <div className="holographic-card p-6 rounded-2xl">
                      <h3 className="text-xl font-bold text-white mb-2">
                        Current Language: {selectedLanguage}
                      </h3>
                      <p className="text-cyan-400/70 mb-4">
                        Change language above and re-upload to translate
                      </p>
                      <button
                        onClick={clearLocalStorage}
                        className="w-full px-4 py-2 bg-red-500/20 border border-red-500/30 rounded-xl text-red-400 hover:bg-red-500/30 transition-colors"
                      >
                        Clear Data & Start Fresh
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
        )}

        {currentView === 'quiz' && processedData && (
          
            <QuizInterface 
              mcqs={processedData.mcqs}
              onAnswer={handleQuizAnswer}
              onBack={() => navigateTo('upload')}
              language={selectedLanguage}
            />
        )}

        {currentView === 'flashcards' && processedData && (
          
            <FlashcardHolo 
              flashcards={processedData.flashcards}
              onStudy={handleFlashcardStudy}
              onBack={() => navigateTo('upload')}
              language={selectedLanguage}
            />
       
        )}

        {currentView === 'progress' && (
          
            <ProgressDashboard 
              progress={progress}
              onBack={() => navigateTo('upload')}
              language={selectedLanguage}
            />
        )}
      </AnimatePresence>

      <Navigation 
        currentView={currentView}
        onNavigate={navigateTo}
        hasData={!!processedData}
      />
    </div>
  )
}