import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

let mixer: THREE.AnimationMixer | null = null;
const actions: Record<string, THREE.AnimationAction> = {};
const animationQueue: string[] = [];
let playing = false;

export function loadAvatar(canvas: HTMLCanvasElement, modelPath: string): void {
  const scene = new THREE.Scene();

  const camera = new THREE.PerspectiveCamera(
    45,
    canvas.clientWidth / canvas.clientHeight,
    0.1,
    100
  );
  camera.position.set(0, 1.5, 3);

  const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
  scene.add(ambientLight);

  const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
  directionalLight.position.set(0, 5, 5);
  scene.add(directionalLight);

  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  renderer.setSize(canvas.clientWidth, canvas.clientHeight);
  renderer.setPixelRatio(window.devicePixelRatio);

  const loader = new GLTFLoader();
  interface GLTFLoadResult {
    scene: THREE.Group;
    animations: THREE.AnimationClip[];
  }

  interface GLTFLoaderCallbacks {
    onLoad: (gltf: GLTFLoadResult) => void;
    onProgress?: (event: ProgressEvent<EventTarget>) => void;
    onError?: (error: ErrorEvent) => void;
  }

  loader.load(
    modelPath,
    (gltf: GLTFLoadResult) => {
      const avatar: THREE.Group = gltf.scene;
      scene.add(avatar);

      mixer = new THREE.AnimationMixer(avatar);
      gltf.animations.forEach((clip: THREE.AnimationClip) => {
        actions[clip.name] = mixer!.clipAction(clip);
      });
    },
    undefined,
    (error: ErrorEvent) => {
      console.error('Error cargando el modelo:', error);
    }
  );

  const clock = new THREE.Clock();
  function animate() {
    requestAnimationFrame(animate);
    const delta = clock.getDelta();
    if (mixer) mixer.update(delta);
    renderer.render(scene, camera);
  }
  animate();
}

export function enqueueAnimation(name: string): void {
  if (!actions[name]) {
    console.warn(`⚠️ Animación '${name}' no encontrada.`);
    return;
  }
  animationQueue.push(name);
  if (!playing) playNext();
}

function playNext(): void {
  if (animationQueue.length === 0) {
    playing = false;
    return;
  }

  const name = animationQueue.shift();
  if (!name || !actions[name]) {
    playing = false;
    return;
  }

  const action = actions[name];
  playing = true;

  action.reset();
  action.setLoop(THREE.LoopOnce, 1);
  action.clampWhenFinished = true;
  action.play();

  const onFinish = () => {
    mixer!.removeEventListener('finished', onFinish);
    playing = false;
    playNext();
  };

  mixer!.addEventListener('finished', onFinish);
}
