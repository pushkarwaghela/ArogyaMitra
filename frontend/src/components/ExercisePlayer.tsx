import React, { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { X, Play, Pause, CheckCircle, Volume2, VolumeX, Loader2 } from 'lucide-react'

interface Exercise {
    id: string
    name: string
    sets: number
    reps: number
    duration?: number
    restTime: number
    videoUrl?: string
    videoTitle?: string
    muscleGroup: string
    difficulty: string
    caloriesBurn: number
}

interface DayWorkout {
    dayNumber: number
    focus: string
}

interface ExercisePlayerProps {
    exercise: Exercise
    dayWorkout: DayWorkout
    onClose: () => void
    onComplete: () => void
}

const ExercisePlayer: React.FC<ExercisePlayerProps> = ({
    exercise,
    dayWorkout,
    onClose,
    onComplete
}) => {
    const [isPlaying, setIsPlaying] = useState(false)
    const [currentSet, setCurrentSet] = useState(1)
    const [repsDone, setRepsDone] = useState(0)
    const [timer, setTimer] = useState(0)
    const [isResting, setIsResting] = useState(false)
    const [restTimer, setRestTimer] = useState(exercise.restTime)
    const [isMuted, setIsMuted] = useState(false)
    const [loadingVideo, setLoadingVideo] = useState(false)
    const [videoError, setVideoError] = useState(false)
    const videoRef = useRef<HTMLIFrameElement>(null)

    useEffect(() => {
        // Load video if URL is provided
        const loadVideo = async () => {
            if (!exercise.videoUrl) {
                setLoadingVideo(true)
                try {
                    // Use a direct YouTube search URL as fallback
                    const searchQuery = encodeURIComponent(`${exercise.name} exercise tutorial proper form`)
                    exercise.videoUrl = `https://www.youtube.com/embed?listType=search&list=${searchQuery}`
                    exercise.videoTitle = `${exercise.name} tutorial`
                } catch (error) {
                    console.error('Failed to load video:', error)
                    setVideoError(true)
                } finally {
                    setLoadingVideo(false)
                }
            }
        }

        loadVideo()
    }, [exercise])

    useEffect(() => {
        let interval: NodeJS.Timeout
        if (isPlaying && !isResting) {
            interval = setInterval(() => {
                setTimer(t => t + 1)
            }, 1000)
        }
        return () => clearInterval(interval)
    }, [isPlaying, isResting])

    useEffect(() => {
        let interval: NodeJS.Timeout
        if (isResting && restTimer > 0) {
            interval = setInterval(() => {
                setRestTimer(t => {
                    if (t <= 1) {
                        setIsResting(false)
                        return exercise.restTime
                    }
                    return t - 1
                })
            }, 1000)
        }
        return () => clearInterval(interval)
    }, [isResting, restTimer, exercise.restTime])

    const handleRepComplete = () => {
        if (repsDone < exercise.reps - 1) {
            setRepsDone(r => r + 1)
        } else {
            if (currentSet < exercise.sets) {
                setCurrentSet(s => s + 1)
                setRepsDone(0)
                setIsResting(true)
                setRestTimer(exercise.restTime)
            } else {
                // Exercise complete
                setIsPlaying(false)
                onComplete()
            }
        }
    }

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60)
        const secs = seconds % 60
        return `${mins}:${secs.toString().padStart(2, '0')}`
    }

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4"
        >
            <div className="bg-gray-900 rounded-2xl w-full max-w-6xl max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="p-4 border-b border-gray-800 flex justify-between items-center">
                    <div>
                        <h2 className="text-xl font-bold text-white">{exercise.name}</h2>
                        <p className="text-gray-400 text-sm">
                            Day {dayWorkout.dayNumber} • {dayWorkout.focus} • Set {currentSet}/{exercise.sets}
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-white"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 p-4">
                    {/* Video Player */}
                    <div className="space-y-4">
                        <div className="aspect-video bg-black rounded-lg overflow-hidden relative">
                            {loadingVideo ? (
                                <div className="w-full h-full flex flex-col items-center justify-center bg-gray-800">
                                    <Loader2 className="w-10 h-10 text-blue-500 animate-spin mb-2" />
                                    <p className="text-gray-400">Loading video...</p>
                                </div>
                            ) : videoError ? (
                                <div className="w-full h-full flex flex-col items-center justify-center bg-gray-800">
                                    <p className="text-gray-400 mb-2">Video unavailable</p>
                                    <p className="text-sm text-gray-500">Follow the instructions below</p>
                                </div>
                            ) : exercise.videoUrl ? (
                                <iframe
                                    ref={videoRef}
                                    src={`${exercise.videoUrl}?autoplay=${isPlaying ? 1 : 0}&mute=${isMuted ? 1 : 0}`}
                                    className="w-full h-full"
                                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                    allowFullScreen
                                    onError={() => setVideoError(true)}
                                    title={exercise.videoTitle || exercise.name}
                                />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center bg-gray-800">
                                    <p className="text-gray-400">No video available</p>
                                </div>
                            )}

                            {/* Video Controls */}
                            {exercise.videoUrl && !loadingVideo && !videoError && (
                                <div className="absolute bottom-4 right-4 flex gap-2">
                                    <button
                                        onClick={() => setIsMuted(!isMuted)}
                                        className="bg-black/50 text-white p-2 rounded-full hover:bg-black/70 transition-colors"
                                        title={isMuted ? "Unmute" : "Mute"}
                                    >
                                        {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
                                    </button>
                                </div>
                            )}
                        </div>

                        {/* Exercise Info */}
                        <div className="bg-gray-800 rounded-lg p-4">
                            <h3 className="text-white font-semibold mb-2">Instructions</h3>
                            <p className="text-gray-300 text-sm">
                                {exercise.sets} sets × {exercise.reps} reps • Rest: {exercise.restTime}s
                            </p>
                            <p className="text-gray-400 text-sm mt-2">
                                Target: {exercise.muscleGroup} • Difficulty: {exercise.difficulty}
                            </p>
                        </div>
                    </div>

                    {/* Tracker */}
                    <div className="space-y-4">
                        <div className="bg-gray-800 rounded-lg p-6">
                            {/* Progress */}
                            <div className="mb-6">
                                <div className="flex justify-between text-sm mb-2">
                                    <span className="text-gray-400">Progress</span>
                                    <span className="text-white font-medium">
                                        Set {currentSet}/{exercise.sets}
                                    </span>
                                </div>
                                <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-green-500 transition-all duration-300"
                                        style={{ width: `${((currentSet - 1) / exercise.sets) * 100}%` }}
                                    />
                                </div>
                            </div>

                            {/* Stats */}
                            <div className="grid grid-cols-3 gap-4 mb-6">
                                <div className="text-center">
                                    <p className="text-3xl font-bold text-white">{repsDone}</p>
                                    <p className="text-xs text-gray-400">Reps Done</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-3xl font-bold text-white">{exercise.reps}</p>
                                    <p className="text-xs text-gray-400">Target</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-3xl font-bold text-white">{formatTime(timer)}</p>
                                    <p className="text-xs text-gray-400">Time</p>
                                </div>
                            </div>

                            {/* Rest Timer */}
                            {isResting && (
                                <div className="bg-orange-500/20 border border-orange-500 rounded-lg p-4 mb-6">
                                    <div className="flex justify-between items-center">
                                        <div>
                                            <p className="text-orange-500 font-semibold">Rest Time</p>
                                            <p className="text-2xl font-bold text-white">{restTimer}s</p>
                                        </div>
                                        <button
                                            onClick={() => setIsResting(false)}
                                            className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
                                        >
                                            Skip
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* Controls */}
                            <div className="flex gap-3">
                                <button
                                    onClick={() => setIsPlaying(!isPlaying)}
                                    className="flex-1 bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-600 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                                    disabled={loadingVideo}
                                >
                                    {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                                    {isPlaying ? 'Pause' : 'Start'}
                                </button>
                                <button
                                    onClick={handleRepComplete}
                                    disabled={isResting || loadingVideo}
                                    className="flex-1 bg-green-500 text-white py-3 rounded-lg hover:bg-green-600 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                                >
                                    <CheckCircle className="w-5 h-5" />
                                    Rep Complete
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    )
}

export default ExercisePlayer