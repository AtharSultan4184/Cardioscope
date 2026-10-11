import { Suspense, useEffect, useRef, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, useGLTF, Html } from '@react-three/drei'
import Artery from './Artery'
import { ARTERY_IDS, MODEL_URL, VIEW_PRESETS } from '../config/anatomy'

// The heart mesh. It also acts as an "occluder": clicks/hovers on it stop there, so you cannot
// accidentally select an artery that is hidden behind the heart.
function HeartModel({ heartRef }) {
  const { scene } = useGLTF(MODEL_URL, false) // false = no Draco decoder download needed
  return (
    <primitive
      ref={heartRef}
      object={scene}
      onClick={(e) => e.stopPropagation()}
      onPointerOver={(e) => e.stopPropagation()}
    />
  )
}
useGLTF.preload(MODEL_URL, false)

// Optional "lub-dub" scale pulse. Applied to heart AND arteries together so they never drift apart.
function BeatGroup({ beat, children }) {
  const ref = useRef()
  useFrame(({ clock }) => {
    if (!ref.current) return
    let s = 1
    if (beat) {
      const t = (clock.elapsedTime % 0.9) / 0.9
      s = 1 + 0.03 * (Math.exp(-(((t - 0.12) / 0.06) ** 2)) + 0.6 * Math.exp(-(((t - 0.38) / 0.08) ** 2)))
    }
    ref.current.scale.setScalar(s)
  })
  return <group ref={ref}>{children}</group>
}

// Moves the camera to a preset when the parent sends a new request ({ name, n }).
function CameraRig({ viewRequest }) {
  const camera = useThree((s) => s.camera)
  const controls = useThree((s) => s.controls)
  useEffect(() => {
    if (!viewRequest) return
    const [x, y, z] = VIEW_PRESETS[viewRequest.name] ?? VIEW_PRESETS.default
    camera.position.set(x, y, z)
    if (controls) { controls.target.set(0, 0, 0); controls.update() } else camera.lookAt(0, 0, 0)
  }, [viewRequest, camera, controls])
  return null
}

function Loader() {
  return (
    <Html center>
      <div className="loading">Loading heart model…</div>
    </Html>
  )
}

/**
 * <HeartViewer />  - the reusable 3D component.
 * props:
 *   risks      { LAD, LCX, RCA } probabilities 0..1 (or null/undefined = no prediction -> grey)
 *   selected   'LAD' | 'LCX' | 'RCA' | null
 *   onSelect   (id|null) => void
 *   beat       boolean            heartbeat pulse
 *   showPoints boolean            show the centre-line control points (calibration)
 *   offset     [x,y,z], scale     nudge the artery group relative to the heart (calibration)
 *   viewRequest { name, n }       camera preset request
 */
export default function HeartViewer({
  risks, selected, onSelect, beat = false, showPoints = false,
  offset = [0, 0, 0], scale = 1, viewRequest,
}) {
  const heartRef = useRef()
  const [hovered, setHovered] = useState(null)

  useEffect(() => {
    document.body.style.cursor = hovered ? 'pointer' : 'auto'
    return () => { document.body.style.cursor = 'auto' }
  }, [hovered])

  return (
    <div className="canvas-wrap">
      <Canvas
        dpr={[1, 1.5]}                       /* cap pixel ratio: keeps it smooth on laptops without a dedicated GPU */
        camera={{ position: VIEW_PRESETS.default, fov: 35, near: 0.1, far: 300 }}
        gl={{ antialias: true }}
        onPointerMissed={() => onSelect?.(null)}
      >
        <color attach="background" args={['#0e1217']} />
        <hemisphereLight args={['#ffffff', '#3a4656', 0.8]} />
        <directionalLight position={[10, 15, 20]} intensity={1.7} />
        <directionalLight position={[-10, 8, -20]} intensity={1.3} />
        <directionalLight position={[0, -15, 5]} intensity={0.4} />

        <OrbitControls makeDefault enableDamping dampingFactor={0.08} minDistance={10} maxDistance={60} />
        <CameraRig viewRequest={viewRequest} />

        <Suspense fallback={<Loader />}>
          <BeatGroup beat={beat}>
            <HeartModel heartRef={heartRef} />
            <group position={offset} scale={scale}>
              {ARTERY_IDS.map((id) => (
                <Artery
                  key={id}
                  id={id}
                  risk={risks?.[id]}
                  selected={selected === id}
                  onSelect={(v) => onSelect?.(v)}
                  onHover={setHovered}
                  showPoints={showPoints}
                  heartRef={heartRef}
                />
              ))}
            </group>
          </BeatGroup>
        </Suspense>
      </Canvas>
    </div>
  )
}
