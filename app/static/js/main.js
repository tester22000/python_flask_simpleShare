$(document).ready(function() {
    // --- 인덱스 페이지 기능 ---
    const contentList = $('#content-list');
    let currentPage = 0;
    let isLoading = false;
    let isLastPage = false;

    // 콘텐츠 로드 함수
    function loadContents() {
        if (isLoading || isLastPage) return;
        isLoading = true;
        $('#loading-spinner').removeClass('hidden');

        const query = $('#search-query').val();
        const type = $('#filter-type').val();

        $.ajax({
            url: "/api/contents",
            data: { page: currentPage, q: query, type: type },
            dataType: 'json',
            success: function(data) {
                $('#loading-spinner').addClass('hidden');
                isLoading = false;

                if (data.length === 0 && currentPage === 0) {
                    contentList.html('<p class="text-center text-gray-500">등록된 콘텐츠가 없습니다.</p>');
                    isLastPage = true;
                    return;
                }
                if (data.length < 10) {
                    isLastPage = true;
                }

                // 콘텐츠 목록 동적으로 추가
                data.forEach(function(content) {
                    const contentHtml = `
                        <div class="bg-white rounded-lg shadow-md p-4 flex items-center justify-between">
                            <div class="flex items-center space-x-4 flex-grow min-w-0">
                                <span class="text-gray-500 font-semibold uppercase text-sm flex-shrink-0">${content.type}</span>
                                <a href="${content.type === 'text' ? '/content/' + content.id : '/download/' + content.id}" class="flex-grow text-blue-600 hover:underline overflow-hidden whitespace-nowrap overflow-ellipsis">
                                    ${content.preview}
                                </a>
                            </div>
                            <div class="flex-shrink-0">
                                <button class="delete-btn text-red-500 hover:text-red-700 transition-colors ml-4" data-id="${content.id}">
                                    <svg class="size-6" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M16.5 4.478v.227a48.842 48.842 0 0 1 3.257.067c.626.084 1.144.364 1.144 1.054a.75.75 0 0 1-.75.75c-1.442 0-3.669-.247-5.594-.247a3.535 3.535 0 0 1-.365 0L12 6.559c-1.845-.231-3.68-.458-5.514-.458a.75.75 0 0 1-.75-.75c0-.69.518-.97 1.144-1.054a48.842 48.842 0 0 1 3.257-.067V4.478a.75.75 0 0 1 .75-.75H12a.75.75 0 0 1 .75.75Z" clip-rule="evenodd" /><path d="M17.25 10.25a.75.75 0 0 1 .75.75v5.5a.75.75 0 0 1-.75.75h-9a.75.75 0 0 1-.75-.75v-5.5a.75.75 0 0 1 .75-.75h9Z" /></svg>
                                </button>
                            </div>
                        </div>
                    `;
                    contentList.append(contentHtml);
                });
                currentPage++;
            },
            error: function() {
                $('#loading-spinner').addClass('hidden');
                isLoading = false;
                console.error("콘텐츠 로드 실패.");
            }
        });
    }

    // 검색/필터 변경 이벤트
    $('#search-query, #filter-type').on('input change', function() {
        currentPage = 0;
        isLastPage = false;
        contentList.empty();
        loadContents();
    });

    // 무한 스크롤 이벤트 (스크롤이 하단에 가까워지면 콘텐츠 로드)
    $(window).scroll(function() {
        if ($(window).scrollTop() + $(window).height() >= $(document).height() - 500) {
            loadContents();
        }
    });

    // 삭제 버튼 클릭 이벤트 (동적으로 추가된 요소에 대해 이벤트 위임)
    $(document).on('click', '.delete-btn', function() {
        if (confirm('정말로 삭제하시겠습니까?')) {
            const contentId = $(this).data('id');
            $.ajax({
                url: `/api/delete/${contentId}`,
                type: 'DELETE',
                success: function() {
                    alert('삭제되었습니다.');
                    location.reload();
                },
                error: function() {
                    alert('삭제에 실패했습니다.');
                }
            });
        }
    });

    // 페이지 로드 시 초기 콘텐츠 로드
    if ($('body').find(contentList).length > 0) {
        loadContents();
    }
    
    // --- 파일 업로드 페이지 기능 ---
    const fileInput = $('#file-input');
    const dragArea = $('#drag-area');

    // 드래그앤드롭 활성화 시
    dragArea.on('dragenter dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).addClass('drag-area-active');
    });

    // 드래그앤드롭 비활성화 시
    dragArea.on('dragleave drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).removeClass('drag-area-active');
    });

    // 파일 드롭 시
    dragArea.on('drop', function(e) {
        e.preventDefault();
        fileInput[0].files = e.originalEvent.dataTransfer.files;
        updateFileName();
    });
    
    // 파일 선택 시
    fileInput.on('change', updateFileName);
    
    // 파일명 업데이트 함수
    function updateFileName() {
        if (fileInput[0].files.length > 0) {
            $('#file-name-display').text(fileInput[0].files[0].name);
        } else {
            $('#file-name-display').text('파일을 선택하거나 드래그하여 놓으세요.');
        }
    }
});