import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';


let mixer: THREE.AnimationMixer;
let actions: { [key: string]: THREE.AnimationAction } = {};
let animationQueue: string[] = [];
let playing = false;

export function loadAvatar(canvas: HTMLCanvasElement, modelPath: string): void {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 600 / 400, 0.1, 100);
  camera.position.z = 3;
  const renderer = new THREE.WebGLRenderer({ canvas });
  renderer.setSize(600, 400);

  const loader = new GLTFLoader();
loader.load(modelPath, (gltf: GLTFLoader.Result) => {
  const avatar = gltf.scene;
  scene.add(avatar);
  mixer = new THREE.AnimationMixer(avatar);
  gltf.animations.forEach((clip: THREE.AnimationClip) => {
    actions[clip.name] = mixer.clipAction(clip);
  });
});


  const clock = new THREE.Clock();
  function animate() {
    requestAnimationFrame(animate);
    const delta = clock.getDelta();
    mixer?.update(delta);
    renderer.render(scene, camera);
  }
  animate();
}

export function enqueueAnimation(name: string): void {
  if (!actions[name]) return;
  animationQueue.push(name);
  if (!playing) playNext();
}

function playNext(): void {
  if (animationQueue.length === 0) {
    playing = false;
    return;
  }
  const name = animationQueue.shift();
  if (!name) return;
  const action = actions[name];
  if (!action) return;
  playing = true;
  action.reset().play().setLoop(THREE.LoopOnce, 1);
  action.clampWhenFinished = true;
  action.getMixer().addEventListener('finished', () => {
    playing = false;
    playNext();
  });
}