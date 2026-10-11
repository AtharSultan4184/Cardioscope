import { useEffect, useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { Html } from '@react-three/drei'
import * as THREE from 'three'
import { ARTERIES, ARTERY_RADIUS as R } from '../config/anatomy'
import { riskToColor, formatPct, isValidProb } from '../lib/risk'

// One coronary artery = a smooth tube along a centre-line, coloured by predicted probability.
// Three meshes: the visible tube, a dark/white outline (so it stands out on the red heart),
// and an invisible fatter tube that makes the thin vessel easy to hover/click.
export default function Artery({ id, risk, selected, onSelect, onHover, showPoints, heartRef }) {
  const spec = ARTERIES[id]

  const geo = useMemo(() => {
    const pts = spec.points.map((p) => new THREE.Vector3(...p))
    const curve = new THREE.CatmullRomCurve3(pts, false, 'centripetal')
    return {
      tube: new THREE.TubeGeometry(curve, 160, R, 14, false),
      outline: new THREE.TubeGeometry(curve, 160, R * 1.55, 14, false),
      hit: new THREE.TubeGeometry(curve, 80, R * 4, 8, false),
      labelPos: curve.getPoint(spec.labelT),
    }
  }, [spec])

  useEffect(() => () => {
    geo.tube.dispose(); geo.outline.dispose(); geo.hit.dispose()
  }, [geo])

  const color = riskToColor(risk)
  const matRef = useRef()

  // High-risk vessels pulse gently; the selected one glows more.
  useFrame(({ clock }) => {
    if (!matRef.current) return
    const base = selected ? 0.55 : 0.3
    const pulse = isValidProb(risk) && risk >= 0.6 ? 0.25 * (0.5 + 0.5 * Math.sin(clock.elapsedTime * 4)) : 0
    matRef.current.emissiveIntensity = base + pulse
  })

  return (
    <group>
      <mesh geometry={geo.tube}>
        <meshStandardMaterial ref={matRef} color={color} emissive={color} roughness={0.35} metalness={0.1} />
      </mesh>

      <mesh geometry={geo.outline}>
        <meshBasicMaterial color={selected ? '#ffffff' : '#0b0f14'} side={THREE.BackSide} />
      </mesh>

      <mesh
        geometry={geo.hit}
        onClick={(e) => {
          if (e.delta > 4) return // it was a drag (rotating), not a click
          e.stopPropagation()
          onSelect(selected ? null : id)
        }}
        onPointerOver={(e) => { e.stopPropagation(); onHover(id) }}
        onPointerOut={() => onHover(null)}
      >
        <meshBasicMaterial transparent opacity={0} depthWrite={false} />
      </mesh>

      {showPoints &&
        spec.points.map((p, i) => (
          <mesh key={i} position={p}>
            <sphereGeometry args={[0.16, 8, 8]} />
            <meshBasicMaterial color="#ffffff" />
          </mesh>
        ))}

      <Html position={geo.labelPos} center occlude={[heartRef]} pointerEvents="none" zIndexRange={[20, 0]}>
        <div className={`artery-label${selected ? ' sel' : ''}`} style={{ borderColor: color }}>
          <b>{id}</b> {formatPct(risk)}
        </div>
      </Html>
    </group>
  )
}
