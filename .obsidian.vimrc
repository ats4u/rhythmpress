
noremap! <C-f> <Right>
noremap! <C-b> <Left>
noremap <C-p> <Up>
noremap <C-n> <Down>

nnoremap <C-W>( <C-W>:tabprevious
nnoremap <C-W>) <C-W>:tabnext
tmap <C-W>( <C-W>:tabprevious
tmap <C-W>) <C-W>:tabnext

" nnoremap <PageUp>   <C-W>:tabp
" nnoremap <PageDown> <C-W>:tabn
" nnoremap <Home>     <C-W>:tabfirst
" nnoremap <End>      <C-W>:tablast
" nnoremap <S-PageUp>   <C-W>:tabm-
" nnoremap <S-PageDown> <C-W>:tabm+
" tmap <PageUp>       <C-W>:tabp
" tmap <PageDown>     <C-W>:tabn
" tmap <Home>         <C-W>:tabfirst
" tmap <End>          <C-W>:tablast
" tmap <S-PageUp>   <C-W>:tabm-
" tmap <S-PageDown> <C-W>:tabm+

noremap <A-ESC> ESC
noremap <A-h> <Left>
noremap <A-j> <Down>
noremap <A-k> <Up>
noremap <A-l> <Right>
noremap <A-s-w> <s-w>
noremap <A-s-b> <s-b>
noremap <A-w> <w>
noremap <A-b> <b>
noremap <A-0> 0
noremap <A-$> $
noremap <A-y> y
noremap <A-d> d
noremap <A-p> p
noremap <A-v> v
noremap <A-s-v> <s-v>
noremap <A-u> u
noremap <A-x> <x>
" g and j
noremap <A-g> g
noremap <A-S-g> <S-g>
" noremap <A-j>   <j>
noremap <A-S-j> <S-j>
noremap <A-C-R> <C-R>
" i o r ( Only Normal mode)
noremap <A-i> i
noremap <A-s-i> <s-i>
noremap <A-o> o
noremap <A-S-o> <s-o>
noremap <A-r> r
noremap <A-S-r> <s-r>

" insert mode
noremap! <A-ESC> <C-o>ESC
noremap! <A-h>   <Left>
noremap! <A-j>   <Down>
noremap! <A-k>   <Up>
noremap! <A-l>   <Right>
noremap! <A-s-w> <C-o><s-w>
noremap! <A-s-b> <C-o><s-b>
noremap! <A-w>   <C-o><w>
noremap! <A-b>   <C-o><b>
noremap! <A-0>   <C-o>0
noremap! <A-$>   <C-o>$
noremap! <A-y>   <C-o>y
noremap! <A-d>   <C-o>d
noremap! <A-p>   <C-o>p
noremap! <A-v>   <C-o>v
noremap! <A-V>   <C-o>V
noremap! <A-S-p> <C-o><S-p>
noremap! <A-u>   <C-o>u
noremap! <A-x>   <C-o><x>
" g and j
noremap! <A-g>   <C-o><g>
noremap! <A-S-g> <C-o><S-g>
" inoremap <A-j>   <C-o><j>
noremap! <A-S-j> <C-o><S-j>
noremap! <A-C-R> <C-o><C-R>

" ？？？？？ "
" <A-h> cannot properly be reassigned with `noremap` command.  I examined the
" problem and found that with `vmap` command it can be assigned.  <A-j> <A-k>
" <A-l> can be reassigned as I expected. The cause of the issue is currently
" unknown.  Ats  (Tue, 22 Feb 2022 14:05:43 +0900)
vmap <A-h> <Left>

" ADDED 2022/01/13 13:01:16
nnoremap <C-p> :cp
nnoremap <C-n> :cn

" enable indentation
set breakindent
" ident by an additional 2 characters on wrapped lines, when line >= 40 characters, put 'showbreak' at start of line
set breakindentopt=shift:-3,min:40
" set showbreak=>>\
set linebreak

" 2021/09/22 13:23:33
set formatoptions+=qoMnm

" ADDED ON 2021/11/28 17:36:44
" default setting from the home
set ai ts=2 sts=2 sw=2 list expandtab
set modeline hls nowrap
set nu
map j gj
map k gk


" ADDED ON 2021/11/28 17:36:44
" for Lisp
nmap <C-S-k> [(
nmap <C-S-j> f(

