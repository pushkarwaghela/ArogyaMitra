import React, { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import {
    X,
    Pause,
    Play as PlayIcon,
    AlertCircle,
    CheckCircle,
    Activity,
    Eye,
    Trophy,
    Camera,
    CameraOff,
    RotateCcw
} from 'lucide-react'
import { toast } from 'react-hot-toast'

interface Exercise {
    id: string
    name: string
    sets: number
    reps: number
    duration?: number
    restTime: number
    videoUrl?: string
    muscleGroup: string
    difficulty: string
    caloriesBurn: number
}

interface DayWorkout {
    day: string
    dayNumber: number
    focus: string
    exercises: Exercise[]
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
    const canvasRef = useRef<HTMLCanvasElement>(null)
    const videoRef = useRef<HTMLVideoElement>(null)
    const streamRef = useRef<MediaStream | null>(null)
    const animationRef = useRef<number>()

    const [isPlaying, setIsPlaying] = useState(false)
    const [cameraActive, setCameraActive] = useState(false)
    const [currentSet, setCurrentSet] = useState(1)
    const [repsDone, setRepsDone] = useState(0)
    const [timer, setTimer] = useState(0)
    const [restTimer, setRestTimer] = useState(0)
    const [isResting, setIsResting] = useState(false)
    const [isCompleted, setIsCompleted] = useState(false)
    const [cameraPermission, setCameraPermission] = useState<boolean | null>(null)
    const [movementDetected, setMovementDetected] = useState(false)
    const [formFeedback, setFormFeedback] = useState<string>('')

    // Timer effect
    useEffect(() => {
        let interval: NodeJS.Timeout
        if (isPlaying && !isResting) {
            interval = setInterval(() => {
                setTimer(prev => prev + 1)
            }, 1000)
        }
        return () => clearInterval(interval)
    }, [isPlaying, isResting])

    // Rest timer effect
    useEffect(() => {
        let interval: NodeJS.Timeout
        if (isResting && restTimer > 0) {
            interval = setInterval(() => {
                setRestTimer(prev => {
                    if (prev <= 1) {
                        setIsResting(false)
                        return 0
                    }
                    return prev - 1
                })
            }, 1000)
        }
        return () => clearInterval(interval)
    }, [isResting, restTimer])

    // Camera setup
    useEffect(() => {
        if (cameraActive) {
            startCamera()
        } else {
            stopCamera()
        }
        return () => stopCamera()
    }, [cameraActive])

    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true })
            streamRef.current = stream
            if (videoRef.current) {
                videoRef.current.srcObject = stream
            }
            setCameraPermission(true)
            startPoseDetection()
        } catch (error) {
            console.error('Camera error:', error)
            setCameraPermission(false)
            toast.error('Unable to access camera')
        }
    }

    const stopCamera = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop())
            streamRef.current = null
        }
        if (animationRef.current) {
            cancelAnimationFrame(animationRef.current)
        }
    }

    const startPoseDetection = () => {
        // Simple motion detection using canvas
        if (!canvasRef.current || !videoRef.current) return

        const canvas = canvasRef.current
        const ctx = canvas.getContext('2d')
        if (!ctx) return

        const detect = () => {
            if (!videoRef.current || !ctx || !cameraActive) return

            // Draw video frame to canvas
            ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height)

            // Simple motion detection (placeholder for actual pose detection)
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
            const data = imageData.data

            // Check average brightness as simple motion indicator
            let brightness = 0
            for (let i = 0; i < data.length; i += 4) {
                brightness += (data[i] + data[i + 1] + data[i + 2]) / 3
            }
            brightness = brightness / (canvas.width * canvas.height)

            // Random form feedback for demo
            if (Math.random() > 0.95) {
                const feedbacks = [
                    'Good form! Keep your back straight',
                    'Slow down, focus on control',
                    'Perfect! Feel the muscle engagement',
                    'Breathe steadily',
                    'Great range of motion'
                ]
                setFormFeedback(feedbacks[Math.floor(Math.random() * feedbacks.length)])
            }

            animationRef.current = requestAnimationFrame(detect)
        }

        detect()
    }

    const handleStart = () => {
        setIsPlaying(true)
        setTimer(0)
        setCurrentSet(1)
        setRepsDone(0)
    }

    const handlePause = () => {
        setIsPlaying(false)
    }

    const handleRepComplete = () => {
        if (repsDone < exercise.reps) {
            setRepsDone(prev => {
                const newReps = prev + 1
                if (newReps >= exercise.reps) {
                    // Set completed
                    if (currentSet < exercise.sets) {
                        // Start rest between sets
                        setIsResting(true)
                        setRestTimer(exercise.restTime)
                        setCurrentSet(prev => prev + 1)
                        setRepsDone(0)
                    } else {
                        // All sets complete
                        setIsCompleted(true)
                        setIsPlaying(false)
                        onComplete()
                        toast.success('Exercise completed! Great job! 🎉')
                    }
                }
                return newReps
            })
        }
    }

    const handleSkipRest = () => {
        setIsResting(false)
        setRestTimer(0)
    }

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60)
        const secs = seconds % 60
        return `${mins}:${secs.toString().padStart(2, '0')}`
    }

    // Add this to load real YouTube videos
    useEffect(() => {
        const loadVideo = async () => {
            try {
                if (exercise.video_url) {
                    setVideoUrl(exercise.video_url)
                } else {
                    // Fetch video from YouTube API
                    const response = await youtubeApi.searchExercise(
                        exercise.name,
                        'workout',
                        'beginner'
                    )
                    if (response.data?.videos?.length > 0) {
                        setVideoUrl(response.data.videos[0].embed_url)
                    }
                }
            } catch (error) {
                console.error('Failed to load video:', error)
            } finally {
                setLoadingVideo(false)
            }
        }

        loadVideo()
    }, [exercise])

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-4"
        >
            <div className="bg-gray-900 rounded-2xl w-full max-w-6xl max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="p-4 border-b border-gray-800 flex justify-between items-center">
                    <div>
                        <h2 className="text-xl font-bold text-white">{exercise.name}</h2>
                        <p className="text-gray-400 text-sm">
                            Day {dayWorkout.dayNumber} • {dayWorkout.focus}
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-white transition-colors"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 p-4">
                    {/* Video Player */}
                    <div className="space-y-4">
                        <div className="aspect-video bg-black rounded-lg overflow-hidden relative">
                            {exercise.videoUrl ? (
                                <iframe
                                    src={exercise.videoUrl}
                                    className="w-full h-full"
                                    allowFullScreen
                                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center bg-gray-800">
                                    <p className="text-gray-400">Video tutorial coming soon</p>
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

                    {/* Camera Feed */}
                    <div className="space-y-4">
                        <div className="relative">
                            <div className="aspect-video bg-gray-800 rounded-lg overflow-hidden">
                                {cameraActive ? (
                                    <>
                                        <video
                                            ref={videoRef}
                                            autoPlay
                                            playsInline
                                            muted
                                            className="w-full h-full object-cover"
                                        />
                                        <canvas
                                            ref={canvasRef}
                                            width={640}
                                            height={480}
                                            className="hidden"
                                        />
                                    </>
                                ) : (
                                    <div className="w-full h-full flex flex-col items-center justify-center">
                                        <Camera className="w-12 h-12 text-gray-600 mb-2" />
                                        <p className="text-gray-500">Camera is off</p>
                                    </div>
                                )}

                                {/* Camera Controls Overlay */}
                                <div className="absolute bottom-4 right-4 flex gap-2">
                                    <button
                                        onClick={() => setCameraActive(!cameraActive)}
                                        className={`p-3 rounded-full ${cameraActive
                                            ? 'bg-red-500 text-white'
                                            : 'bg-gray-700 text-gray-300'
                                            } hover:scale-110 transition-transform`}
                                    >
                                        {cameraActive ? <CameraOff className="w-5 h-5" /> : <Camera className="w-5 h-5" />}
                                    </button>
                                </div>

                                {/* Form Feedback */}
                                {formFeedback && cameraActive && (
                                    <div className="absolute top-4 left-4 right-4">
                                        <div className="bg-blue-500 text-white px-4 py-2 rounded-lg text-sm flex items-center gap-2">
                                            <Activity className="w-4 h-4" />
                                            {formFeedback}
                                        </div>
                                    </div>
                                )}
                            </div>

                            {cameraPermission === false && (
                                <div className="mt-2 bg-red-900/50 text-red-300 p-3 rounded-lg flex items-center gap-2">
                                    <AlertCircle className="w-5 h-5" />
                                    <p className="text-sm">Camera access denied. Please enable camera for form feedback.</p>
                                </div>
                            )}
                        </div>

                        {/* Workout Controls */}
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
                                        style={{
                                            width: `${((currentSet - 1) / exercise.sets) * 100}%`
                                        }}
                                    />
                                </div>
                            </div>

                            {/* Stats */}
                            <div className="grid grid-cols-3 gap-4 mb-6">
                                <div className="text-center">
                                    <p className="text-3xl font-bold text-white">{repsDone}</p>
                                    <p className="text-xs text-gray-400">Reps</p>
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
                                            onClick={handleSkipRest}
                                            className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
                                        >
                                            Skip
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* Action Buttons */}
                            {!isCompleted ? (
                                <div className="flex gap-3">
                                    {!isPlaying ? (
                                        <button
                                            onClick={handleStart}
                                            className="flex-1 bg-green-500 text-white py-3 rounded-lg hover:bg-green-600 transition-colors flex items-center justify-center gap-2"
                                        >
                                            <PlayIcon className="w-5 h-5" />
                                            {currentSet === 1 ? 'Start' : 'Resume'}
                                        </button>
                                    ) : (
                                        <button
                                            onClick={handlePause}
                                            className="flex-1 bg-yellow-500 text-white py-3 rounded-lg hover:bg-yellow-600 transition-colors flex items-center justify-center gap-2"
                                        >
                                            <Pause className="w-5 h-5" />
                                            Pause
                                        </button>
                                    )}
                                    <button
                                        onClick={handleRepComplete}
                                        disabled={isResting}
                                        className="flex-1 bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-600 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                                    >
                                        <CheckCircle className="w-5 h-5" />
                                        Rep Complete
                                    </button>
                                </div>
                            ) : (
                                <div className="bg-green-500/20 border border-green-500 rounded-lg p-4 text-center">
                                    <Trophy className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
                                    <p className="text-green-400 font-semibold">Exercise Complete!</p>
                                    <p className="text-gray-300 text-sm mt-1">
                                        Great job! You've completed this exercise.
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    )
}

export default ExercisePlayer