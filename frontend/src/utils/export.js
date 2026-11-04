import { getBookCardPng, getQuizCardPng } from '../api/client'
import { paceLabel } from './format'

const dateRu = (iso) =>
  new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })

export function saveBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

export function saveText(text, filename) {
  // BOM, чтобы Блокнот Windows правильно открыл кириллицу
  saveBlob(new Blob(['﻿', text], { type: 'text/plain;charset=utf-8' }), filename)
}

const safeName = (s) => String(s).replace(/[\\/:*?"<>|]+/g, '').trim().slice(0, 60) || 'book'

export function bookLine(book, i) {
  const tags = (book.tags || []).map((t) => t.name).join(', ')
  const head = `${i + 1}. ${book.title} — ${book.author}`
  const meta = [book.page_count ? `${book.page_count} стр.` : null, book.pace ? `темп: ${paceLabel(book.pace)}` : null]
    .filter(Boolean).join(', ')
  return [head, tags && `   Теги: ${tags}`, meta && `   ${meta}`, book.description && `   ${book.description}`]
    .filter(Boolean).join('\n')
}

export function quizToText(session) {
  const a = session.answers || {}
  const labels = { mood: 'Настроение', genre: 'Жанр', pace: 'Темп', length: 'Длина' }
  const answers = Object.entries(a).map(([k, v]) => `${labels[k] || k}: ${v}`).join('; ')
  return [
    'BookMatch — моя подборка',
    `Дата: ${dateRu(session.created_at)}`,
    answers && `Ответы: ${answers}`,
    '',
    ...session.result_books.map(bookLine).flatMap((l) => [l, '']),
  ].filter((l) => l !== false && l !== undefined).join('\n')
}

export function exportQuiz(session) {
  const day = new Date(session.created_at).toISOString().slice(0, 10)
  saveText(quizToText(session), `bookmatch-podborka-${day}.txt`)
}

export function exportLibrary(library, comments = []) {
  const byBook = {}
  comments.forEach((c) => { (byBook[c.book_id] ||= []).push(c.text) })
  const section = (title, books) => [
    `${title} (${books.length})`,
    ...books.flatMap((b, i) => [
      bookLine(b, i),
      ...(byBook[b.id] || []).map((t) => `   Моя заметка: ${t}`),
      '',
    ]),
  ]
  const text = [
    'BookMatch — моя библиотека',
    `Дата: ${dateRu(new Date().toISOString())}`,
    '',
    ...section('Прочитано', library.read),
    ...section('Хочу прочитать', library.wishlist),
  ].join('\n')
  saveText(text, 'bookmatch-biblioteka.txt')
}

export function exportBookText(book) {
  saveText(bookLine(book, 0).replace(/^1\. /, ''), `${safeName(book.title)}.txt`)
}

export async function exportBookPng(book) {
  const { data } = await getBookCardPng(book.id)
  saveBlob(data, `${safeName(book.title)}.png`)
}

export async function exportQuizPng(session) {
  const { data } = await getQuizCardPng(session.id)
  const day = new Date(session.created_at).toISOString().slice(0, 10)
  saveBlob(data, `bookmatch-podborka-${day}.png`)
}
