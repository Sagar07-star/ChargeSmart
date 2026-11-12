import {describe,it,expect} from 'vitest';
import {usableRange} from './types';
describe('battery reserve',()=>{it('uses energy above reserve only',()=>expect(usableRange(45,35,15,.16)).toBeCloseTo(56.25));it('never returns negative range',()=>expect(usableRange(45,10,15,.16)).toBe(0))});
